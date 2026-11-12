// Copyright 2024-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#include "TestThreadPoolExecutor.h"
#include "TimeOutput.h"

#include <scene_rdl2/common/rec_time/RecTime.h>

#include <algorithm>
#include <atomic>
#include <thread>
#include <chrono>
#include <vector>

#ifndef PLATFORM_APPLE
#include <pthread.h> // pthread_getaffinity_np
#include <sched.h> // sched_getaffinity
#endif // end of Not PLATFORM_APPLE

// This directive should not commented out for the release version.
// This is only used for local debugging purposes.
//#define ENDURANCE_TEST

namespace scene_rdl2 {
namespace threadPoolExecutor {
namespace unittest {

void
TestThreadPoolExecutor::testBootAndShutdown()
{
    TIME_START;

    std::cerr << "TestThreadPoolExecutor.cc testBootAndShutdown() start\n";

#ifdef ENDURANCE_TEST
    // Tested on cobaltcard
    constexpr float maxTestDurationSec = 240.0f; // 4 min
    constexpr int maxLoop = 10000;
#else // else ENDURANCE_TEST
    constexpr float maxTestDurationSec = 4.0f;
    constexpr int maxLoop = 10;
#endif // end else ENDURANCE_TEST

    bootWatcher(maxTestDurationSec);

    bootAndShutdownLoop("no-CPU-Affinity", maxLoop, nullptr);
    bootAndShutdownLoop("CPU-Affinity", maxLoop, [](size_t id) -> unsigned { return static_cast<unsigned>(id); });

    shutdownWatcher();

    std::cerr << "TestThreadPoolExecutor.cc testBootAndShutdown() finish\n";    
    TIME_END;
}

void
TestThreadPoolExecutor::testCurrentThreadId()
// Inside tasks getCurrentThreadId() gives every pool thread id exactly once, and it is
// kNotPoolThread on a thread that is not in the pool.
{
    TIME_START;

    constexpr size_t threadTotal = 8;

    CPPUNIT_ASSERT("caller is not a pool thread" &&
                   ThreadPoolExecutor::getCurrentThreadId() == ThreadPoolExecutor::kNotPoolThread);

    ThreadPoolExecutor pool(threadTotal);
    std::vector<size_t> idOfTask(threadTotal, ThreadPoolExecutor::kNotPoolThread);
    std::atomic<size_t> started {0};
    for (size_t task = 0; task < threadTotal; ++task) {
        pool.run([&, task]() {
            ++started;
            while (started < threadTotal) { // keep every pool thread busy with exactly one task
                std::this_thread::yield();
            }
            idOfTask[task] = ThreadPoolExecutor::getCurrentThreadId();
        });
    }
    pool.wait();

    std::vector<int> seen(threadTotal, 0);
    for (const size_t id : idOfTask) {
        CPPUNIT_ASSERT("id is in range" && id < threadTotal);
        ++seen[id];
    }
    for (const int count : seen) {
        CPPUNIT_ASSERT("every pool thread id is used exactly once" && count == 1);
    }

    TIME_END;
}

namespace {

struct TaskResult
{
    size_t mThreadId {ThreadPoolExecutor::kNotPoolThread};
    unsigned mPinnedCpuId {ThreadPoolExecutor::kNotPinnedCpuId};
    bool mAffinityIsPinnedCpuOnly {false}; // OS affinity of the thread is exactly mPinnedCpuId
};

// Runs exactly one task on every pool thread and returns what each task observed.
std::vector<TaskResult>
runOneTaskPerThread(const size_t threadTotal, const ThreadPoolExecutor::CalcCpuIdFunc& cpuIdFunc)
{
    ThreadPoolExecutor pool(threadTotal, cpuIdFunc);
    std::vector<TaskResult> resultTbl(threadTotal);
    std::atomic<size_t> started {0};
    for (size_t task = 0; task < threadTotal; ++task) {
        pool.run([&, task]() {
            ++started;
            while (started < threadTotal) { // keep every pool thread busy with exactly one task
                std::this_thread::yield();
            }
            TaskResult& result = resultTbl[task];
            result.mThreadId = ThreadPoolExecutor::getCurrentThreadId();
            result.mPinnedCpuId = ThreadPoolExecutor::getCurrentPinnedCpuId();
#           ifndef PLATFORM_APPLE
            cpu_set_t cpuSet;
            CPU_ZERO(&cpuSet);
            if (pthread_getaffinity_np(pthread_self(), sizeof(cpuSet), &cpuSet) == 0 &&
                result.mPinnedCpuId < CPU_SETSIZE) {
                result.mAffinityIsPinnedCpuOnly =
                    (CPU_COUNT(&cpuSet) == 1) && CPU_ISSET(result.mPinnedCpuId, &cpuSet);
            }
#           endif // end of Not PLATFORM_APPLE
        });
    }
    pool.wait();
    return resultTbl;
}

#ifndef PLATFORM_APPLE

// CPU ids this process may run on and that CpuAffinityMask can express (< hardware_concurrency).
std::vector<unsigned>
getAllowedCpuIdTbl()
{
    std::vector<unsigned> cpuIdTbl;
    cpu_set_t cpuSet;
    CPU_ZERO(&cpuSet);
    if (sched_getaffinity(0, sizeof(cpuSet), &cpuSet) != 0) return cpuIdTbl;

    const unsigned cpuIdEnd = std::min<unsigned>(std::thread::hardware_concurrency(), CPU_SETSIZE);
    for (unsigned cpuId = 0; cpuId < cpuIdEnd; ++cpuId) {
        if (CPU_ISSET(cpuId, &cpuSet)) cpuIdTbl.push_back(cpuId);
    }
    return cpuIdTbl;
}

#endif // end of Not PLATFORM_APPLE

} // namespace

void
TestThreadPoolExecutor::testCurrentPinnedCpuId()
// getCurrentPinnedCpuId() returns the CPU id requested by cpuIdFunc for the calling pool thread, and
// kNotPinnedCpuId outside the pool, without cpuIdFunc, or on Apple. This test does not depend on the
// NUMA topology of the machine.
{
    TIME_START;

    constexpr size_t threadTotal = 4;

    CPPUNIT_ASSERT("caller is not pinned by a pool" &&
                   ThreadPoolExecutor::getCurrentPinnedCpuId() == ThreadPoolExecutor::kNotPinnedCpuId);

    for (const TaskResult& result : runOneTaskPerThread(threadTotal, nullptr)) {
        CPPUNIT_ASSERT("no cpuIdFunc means not pinned" &&
                       result.mPinnedCpuId == ThreadPoolExecutor::kNotPinnedCpuId);
    }

#   ifdef PLATFORM_APPLE
    for (const TaskResult& result : runOneTaskPerThread(threadTotal, [](size_t id) -> unsigned { return static_cast<unsigned>(id); })) {
        CPPUNIT_ASSERT("CPU pinning is not supported on Apple" &&
                       result.mPinnedCpuId == ThreadPoolExecutor::kNotPinnedCpuId);
    }
#   else // else of PLATFORM_APPLE
    const std::vector<unsigned> allowedCpuIdTbl = getAllowedCpuIdTbl();
    if (!allowedCpuIdTbl.empty()) { // nothing to pin to if the allowed CPU set is unknown
        const size_t pinnedThreadTotal = std::min(threadTotal, allowedCpuIdTbl.size());
        const std::vector<TaskResult> resultTbl =
            runOneTaskPerThread(pinnedThreadTotal,
                                [&](size_t threadId) -> unsigned { return allowedCpuIdTbl[threadId]; });

        std::vector<unsigned> pinnedCpuIdTbl;
        for (const TaskResult& result : resultTbl) {
            CPPUNIT_ASSERT("threadId is in range" && result.mThreadId < pinnedThreadTotal);
            CPPUNIT_ASSERT("pinned cpuId is the one requested for this threadId" &&
                           result.mPinnedCpuId == allowedCpuIdTbl[result.mThreadId]);
            CPPUNIT_ASSERT("OS affinity of the thread is the pinned cpuId only" &&
                           result.mAffinityIsPinnedCpuOnly);
            pinnedCpuIdTbl.push_back(result.mPinnedCpuId);
        }

        std::sort(pinnedCpuIdTbl.begin(), pinnedCpuIdTbl.end());
        CPPUNIT_ASSERT("every pool thread has a different pinned cpuId" &&
                       std::adjacent_find(pinnedCpuIdTbl.begin(), pinnedCpuIdTbl.end()) == pinnedCpuIdTbl.end());
    }
#   endif // end of Not PLATFORM_APPLE

    TIME_END;
}

void
TestThreadPoolExecutor::bootAndShutdownLoop(const std::string& msg,
                                            const int maxLoop,
                                            const ThreadPoolExecutor::CalcCpuIdFunc& calcCpuIdFunc) const
{
    unsigned threadTotal = std::thread::hardware_concurrency();

    std::cerr << msg << " {\n";
    for (int loopId = 0; loopId < maxLoop; ++loopId) {
        std::cerr << "  loopId:" << loopId << '/' << maxLoop - 1 << " threadTotal:" << threadTotal << '\n';

        ThreadPoolExecutor pool(threadTotal, calcCpuIdFunc);
        CPPUNIT_ASSERT(pool.testBootShutdown());
    }
    std::cerr << "}\n";
}

//------------------------------------------------------------------------------------------
    
void
TestThreadPoolExecutor::bootWatcher(const float maxTestDurationSec)
{
    mWatcherThreadState = ThreadState::INIT; // just in case
    mWatcherThread = std::move(std::thread([&] { watcherThreadMain(maxTestDurationSec); }));

    { // Wait until thread is booted
        std::unique_lock<std::mutex> uqLock(mWatcherMutex);
        mCvWatcherBoot.wait(uqLock, [&]() {
                return (mWatcherThreadState != ThreadState::INIT); // Not wait if already non INIT condition 
           });
    }
}

void
TestThreadPoolExecutor::watcherThreadMain(const float maxTestDurationSec)
//
// This thread is watching the test thread is properly finished under the expected time duration.
// If the time exceeds the limit, the process exits itself. This is important to keep unitTest
// finished under a constant period.
//    
{
    // First of all change threadState condition and do notify_one to caller
    {
        std::lock_guard<std::mutex> lock(mWatcherMutex);
        mWatcherThreadState = ThreadState::IDLE;
    }
    mCvWatcherBoot.notify_one(); // notify to ThreadExecutor constructor
    
    rec_time::RecTime recTime;
    recTime.start();

    while (true) {
        if (mWatcherThreadShutdown) break;
        if (recTime.end() >= maxTestDurationSec) {
            std::cerr << "ERROR : watcherThread detected too long test execution."
                      << " duration:" << maxTestDurationSec << " sec\n";
            exit(1);
        }
        std::this_thread::sleep_for(std::chrono::microseconds(10000));
    }

    std::cerr << ">> Watcher thread shutdown <<\n";
}

void
TestThreadPoolExecutor::shutdownWatcher()
{
    mWatcherThreadShutdown = true;
    mWatcherThread.join();
}

} // namespace unittest
} // namespace threadPoolExecutor
} // namespace scene_rdl2
