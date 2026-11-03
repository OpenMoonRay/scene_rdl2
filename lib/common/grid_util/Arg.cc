// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#include "Arg.h"
#include "TlSvr.h"

#include <scene_rdl2/render/util/StrUtil.h>

#include <cctype>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <utility>

namespace scene_rdl2 {
namespace grid_util {

Arg::Arg(const std::string& cmdLine, TlSvr* tlSvr) :
    mCurrArgId(0),
    mNextId(1),
    mTlSvr(tlSvr),
    mCerrOutput(true),
    mMsgHandler(nullptr)
{
    setupOrg(cmdLine);
    setupArg(cmdLine);

    mComName = mOrg[0];
}

Arg::Arg(const std::string& cmdName, const std::string& argLine, TlSvr* tlSvr) :
    mComName(cmdName),
    mCurrArgId(0),
    mNextId(2),
    mTlSvr(tlSvr),
    mCerrOutput(true),
    mMsgHandler(nullptr)
{
    setupOrg(cmdName + ' ' + argLine);
    setupArg(argLine);
}

Arg::Arg(int argc, char** argv, TlSvr* tlSvr) :
    mCurrArgId(0),
    mNextId(0),
    mTlSvr(tlSvr),
    mCerrOutput(true),
    mMsgHandler(nullptr)
{
    for (int i = 0; i < argc; ++i) {
        mArg.emplace_back(argv[i]);
        mOrg.emplace_back(argv[i]);
    }

    shiftArg();
    if (!mOrg.empty()) mComName = mOrg[0]; // argc might be 0
}

Arg
Arg::childArg()
{
    return makeChildArg([&]() -> std::string { return childCmdNameGen(); });
}

Arg
Arg::childArg(const std::string& comName)
{
    return makeChildArg([&]() -> std::string { return comName; });
}

std::string
Arg::currArgCmdLine() const
{
    std::ostringstream ostr;
    for (size_t i = 0; i < size(); ++i) {
        ostr << escapeComment(mArg[i]);
        if (i != size() - 1) ostr << ' ';
    }
    return ostr.str();
}

bool
Arg::noNeedToEvalTest(bool parserHasArg) const
//
// Parser object consists of option definitions and argument definitions (See Parser.h comment). Option
// definition looks like "optA <A> <B>" and Argument definition looks like "<A> <B>" (i.e. an Option
// definition without an option name). This parserHasArg flag indicates whether the Parser object has an
// Argument type definition or not.
//
{
    if (emptyArg() && mComName.empty()) {
        // completely empty input

        if (!parserHasArg) {
            // Parser does not have an argument definition and this Arg does not have any arguments
            // as well. So, we can safely return true (= no need to evaluate this arg).
            return true;
        }

        // This is an empty Arg but a potential error case. Parser has argument definitions
        // and we can not skip evaluation of this Arg.
    }
    return false;
}

bool
Arg::isOpt(const std::vector<std::string>& nameTbl, bool caseSensitive)
{
    for (const auto& itr: nameTbl) {
        if (isOpt(itr, caseSensitive)) return true;
    }
    return false;
}

void
Arg::shiftArgAll()
{
    do {
        shiftArg();
    } while (!emptyArg());
}

std::string
Arg::warnMsgPrevVal(const std::string& msg) const
{
    return errMsg("WARNING : ", msg, -1);
}

std::string
Arg::warnMsgCurrVal(const std::string& msg) const
{
    return errMsg("WARNING : ", msg, 0);
}

std::string
Arg::warnMsgLastNext(const std::string& msg) const
{
    return errMsg("WARNING : ", msg, static_cast<int>(size()));
}

std::string
Arg::warnMsgEvalOpt(const std::string& msg) const
{
    if (mComName.empty()) {
        return msg + " optName:" + mCurrOptName; // special case for top level parsing
    } else {
        return msg + " comName:" + mComName + " optName:" + mCurrOptName;
    }
}

std::string
Arg::warnMsgEvalArg(const std::string& msg) const
{
    if (mComName.empty()) {
        return msg + " argId:" + std::to_string(mCurrArgId); // special case for top level parsing
    } else {
        return msg + " comName:" + mComName + " argId:" + std::to_string(mCurrArgId);
    }
}

bool
Arg::msg(const std::string& msg) const
{
    bool flag = true;

    if (mCerrOutput) {
        // output string to cerr
        std::cerr << msg;
    }

    if (mTlSvr) {
        // output to TlSvr if necessary
        if (!mTlSvr->send(msg)) flag = false; // blocking function
    }

    // output to msgHandler if necessary
    if (mMsgHandler) {
        if (!(mMsgHandler)(msg)) flag = false;
    }

    return flag;
}

bool
Arg::fmtMsg(const char* fmt, ...) const
{
    if (std::string(fmt).empty()) return true;

    bool st(true);

    va_list ap;
    va_start(ap, fmt);
    {
        st = vaMsg(fmt, ap);
    }
    va_end(ap);

    return st;
}

std::string
Arg::show() const
{
    std::ostringstream ostr;
    ostr << "Arg {\n"
         << "  mComName:" << mComName << '\n'
         << "  mCurrOptName:" << mCurrOptName << '\n'
         << "  mCurrArgId:" << mCurrArgId << '\n'
         << "  mNextId:" << mNextId << '\n'
         << scene_rdl2::str_util::addIndent(showArgTbl("mArg", mArg)) << '\n'
         << scene_rdl2::str_util::addIndent(showArgTbl("mOrg", mOrg)) << '\n'
         << "  mTlSvr:0x" << std::hex << (uintptr_t)mTlSvr << std::dec << '\n'
         << "  mCerrOutput:" << (mCerrOutput ? "true" : "false") << '\n'
         << "}";
    return ostr.str();
}

bool
Arg::verify(const std::string& comName,
            const std::string& currOptName,
            size_t currArgId,
            size_t nextId,
            const ArgTbl& arg,
            const ArgTbl& org)
//
// This function is designed for unit testing
//
{
    auto isSameStrVec = [](const ArgTbl& a, const ArgTbl& b) {
        if (a.size() != b.size()) return false;
        for (size_t i = 0; i < a.size(); ++i) {
            if (a[i] != b[i]) return false;
        }
        return true;
    };

    if (mComName != comName ||
        mCurrOptName != currOptName ||
        mCurrArgId != currArgId ||
        !isSameStrVec(mArg, arg) ||
        mNextId != nextId ||
        !isSameStrVec(mOrg, org)) {
        return false;
    }
    return true;
}

//------------------------------------------------------------------------------------------

Arg
Arg::makeChildArg(const std::function<std::string()>& childCmdNameGenFunc)
{
    Arg arg;

    arg.mNextId = mNextId;
    arg.mTlSvr = mTlSvr;
    arg.mMsgHandler = mMsgHandler;
    arg.mCerrOutput = mCerrOutput;

    // mArg is already shifted. Comments (words after '#') are removed at construction time only for
    // command line string input. The argc/argv input does not treat '#' specially.
    arg.mArg = mArg;
    arg.mOrg = mOrg;
    arg.mComName = (childCmdNameGenFunc)();

    shiftArgAll(); // shift all for original arg

    return arg;
}

void
Arg::setupOrg(const std::string& cmdLine)
{
    // First argument (i.e. command name) is empty in this case because this is a top level command line
    mOrg.emplace_back(""); // empty first entry

    for (auto& word: splitCmdLine(cmdLine, true)) {
        mOrg.emplace_back(std::move(word));
    }
}

void
Arg::setupArg(const std::string& cmdLine)
{
    mArg = splitCmdLine(cmdLine, false);
}

void
Arg::shiftArg()
{
    if (!mArg.size()) return;

    for (size_t i = 1; i < mArg.size(); ++i) {
        mArg[i - 1] = std::move(mArg[i]);
    }
    mArg.pop_back();
    mNextId++;
}

std::string
Arg::errMsg(const std::string& msgTitle,
            const std::string& msg,
            int errArgIdOffset) const
{
    std::ostringstream ostr;
    ostr << msgTitle << msg << " {\n"
         << "  " << getCmdLine() << '\n'
         << "} " << getErrorCmdLine(mNextId + errArgIdOffset);
    return ostr.str();
}

std::string
Arg::getCmdLine() const
{
    std::ostringstream ostr;
    for (size_t i = 0 ; i < mOrg.size(); ++i) {
        ostr << mOrg[i];
        if (i != mOrg.size() - 1) ostr << ' ';
    }
    return ostr.str();
}

std::string
Arg::getErrorCmdLine(const size_t argId) const
{
    std::ostringstream ostr;
    for (size_t i = 0; i < mOrg.size(); ++i) {
        ostr << strGen(((i != argId) ? ' ' : '^'), mOrg[i].size());
        if (i == argId) break;
        if (i != mOrg.size() - 1) ostr << ' ';
    }
    if (argId >= mOrg.size()) ostr << " ^^^";
    return ostr.str();
}

std::string
Arg::strGen(const char c, const size_t size) const
{
    std::ostringstream ostr;
    for (size_t i = 0; i < size; ++i) { ostr << c; }
    return ostr.str();
}

std::string
Arg::childCmdNameGen() const
{
    std::string name;
    if (mNextId > 0 && mNextId <= mOrg.size()) {
        if (!mComName.empty()) name = mComName + ' ';
        name += mOrg[mNextId - 1]; // last consumed word. mOrg might include comment words
    } else {
        name = mComName;
    }
    return name;
}

std::string
Arg::showArgTbl(const std::string& msg, const ArgTbl& tbl) const
{
    std::ostringstream ostr;
    ostr << msg << " total:" << tbl.size() << " {\n";
    for (size_t i = 0; i < tbl.size(); ++i) {
        ostr << "  i:" << i << ' ' << tbl[i] << '\n';
    }
    ostr << "}";
    return ostr.str();
}

Arg::ArgTbl
Arg::splitCmdLine(const std::string& cmdLine, const bool includeComment) const
//
// Split the command line into words by blanks (including NL).
// '#' starts a comment unless it is escaped by '\' (i.e. "\#" is a literal '#' in a word). Other '\' are
// literal. Every word after the comment start is only returned if includeComment is true. The comment
// part is not escape processed because it is kept only for message display.
//
{
    ArgTbl tbl;
    std::string word;
    bool inComment = false;

    auto flushWord = [&]() {
        if (!word.empty()) {
            tbl.push_back(std::move(word));
            word.clear();
        }
    };

    for (size_t i = 0; i < cmdLine.size(); ++i) {
        const char c = cmdLine[i];
        if (!inComment && c == '\\' && i + 1 < cmdLine.size() && cmdLine[i + 1] == '#') {
            word.push_back('#'); // escaped '#'
            ++i;
        } else if (c == '#' && !inComment) {
            flushWord();
            if (!includeComment) break;
            inComment = true;
            word.push_back(c);
        } else if (std::isspace(static_cast<unsigned char>(c))) {
            flushWord();
        } else {
            word.push_back(c);
        }
    }
    flushWord();

    return tbl;
}

std::string
Arg::escapeComment(const std::string& str)
{
    std::string out;
    for (const char c: str) {
        if (c == '#') out.push_back('\\');
        out.push_back(c);
    }
    return out;
}

bool
Arg::vaMsg(const char* fmt, va_list ap) const
{
    // figure out proper buffer size
    int buffSize = 0;
    {
        va_list tmpAp;
        va_copy(tmpAp, ap); // we have to use va_copy in order to keep original ap
        buffSize = std::vsnprintf(nullptr, 0, fmt, tmpAp);
        va_end(tmpAp);
    }
    if (buffSize < 0) return false; // formatting error

    std::string msgBuff(buffSize + 1, 0x0); // +1 is for terminator NULL

    // create string from va_list
    if (std::vsnprintf(static_cast<char *>(&msgBuff[0]),
                       msgBuff.size(),
                       fmt,
                       ap) != buffSize) {
        return false;
    }
    msgBuff.resize(buffSize); // resize to actual length (without terminator NULL)

    return msg(msgBuff);
}

bool
Arg::cmpOpt(const std::string& a, const std::string& b, bool caseSensitive) const
{
    std::string workA, workB;
    if (caseSensitive) {
        workA = a;
        workB = b;
    } else {
        workA = str_util::upperStr(a);
        workB = str_util::upperStr(b);
    }

    if (workA == workB) return true;

    if (workA[0] == '-') {
        if (workA.substr(1) == workB) return true;
    } else if (workB[0] == '-') {
        if (workA == workB.substr(1)) return true;
    }
    return false;
}

// static function
bool
Arg::isBool(const std::string& str)
{
    using StrTbl = std::vector<std::string>;
    auto multiEq = [&](const StrTbl& tbl) {
        for (const auto& itr: tbl) {
            if (str_util::upperStr(str) == str_util::upperStr(itr)) return true;
        }
        return false;
    };
    return multiEq(StrTbl{"true", "t", "on", "1"}); // non case sensitive
}

} // namespace grid_util
} // namespace scene_rdl2
