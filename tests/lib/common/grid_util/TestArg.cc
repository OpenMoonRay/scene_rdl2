// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#include "TestArg.h"
#include "TimeOutput.h"

#include <iostream>
#include <sstream>
#include <streambuf>
#include <string>
#include <string.h>

namespace scene_rdl2 {
namespace grid_util {
namespace unittest {

namespace {

class CerrCapture
//
// Purpose:
//   Arg::msg() writes to std::cerr when mCerrOutput is true. We want to verify this real output behavior
//   (i.e. whether the message actually reaches std::cerr) instead of checking an internal flag through
//   a string search of Arg::show() output. Arg has no getter for mCerrOutput and we do not want to add
//   one just for the test.
//
// How it works:
//   std::cerr is a stream object which only formats data. Where the data really goes is decided by
//   the stream buffer (std::streambuf) attached to it. std::ostream::rdbuf(newBuf) swaps this buffer
//   and returns the previous one.
//   - Constructor : attach the buffer of a local std::ostringstream to std::cerr and remember the original
//                   buffer. From now on, everything written to std::cerr is stored in the ostringstream
//                   (nothing appears on the real terminal).
//   - str()       : return the captured text.
//   - Destructor  : put the original buffer back. Because this is done by a destructor (RAII), std::cerr
//                   is restored properly even if CPPUNIT_ASSERT throws. Otherwise std::cerr would be left
//                   pointing to a destroyed buffer and break all later output.
//   Note: mBuf is declared before mOrigBuf because mOrigBuf's initializer uses mBuf. The destructor body runs
//   before the members are destroyed, so std::cerr is always restored before mBuf goes away.
//
{
public:
    CerrCapture() : mOrigBuf(std::cerr.rdbuf(mBuf.rdbuf())) {}
    ~CerrCapture() { std::cerr.rdbuf(mOrigBuf); }

    CerrCapture(const CerrCapture&) = delete;
    CerrCapture& operator =(const CerrCapture&) = delete;

    std::string str() const { return mBuf.str(); }

private:
    std::ostringstream mBuf;
    std::streambuf* mOrigBuf;
};

} // namespace

void
TestArg::testRealToleranceCompare()
{
    TIME_START;

    {
        const float a = 1.234;
        const float b = 1.2340001;
        /* for debug
        std::cerr << real_util::floatDump(a) << '\n'
                  << real_util::floatDump(b) << '\n';
        */
        // float dump 'a' {
        //   val:1.234
        //   hex:0x3f9df3b6
        //   bit:0011-1111-1001-1101 1111-0011-1011-0110
        // }
        // float dump 'b' {
        //   val:1.234
        //   hex:0x3f9df3b7
        //   bit:0011-1111-1001-1101 1111-0011-1011-0111
        // }
        CPPUNIT_ASSERT("float tolerance compare testA" &&
                       !real_util::floatToleranceEqual(a, b, real_util::compareMaskGen32(0)));
        CPPUNIT_ASSERT("float tolerance compare testB" &&
                       real_util::floatToleranceEqual(a, b, real_util::compareMaskGen32(1)));
    }
    {
        const float a = -12.34;
        const float b = -12.340002;
        /* for debug
        std::cerr << real_util::floatDump(a) << '\n'
                  << real_util::floatDump(b) << '\n';
        */
        // float dump 'a' {
        //   val:-12.34
        //   hex:0xc14570a4
        //   bit:1100-0001-0100-0101 0111-0000-1010-0100
        // }
        // float dump 'b' {
        //   val:-12.34
        //   hex:0xc14570a6
        //   bit:1100-0001-0100-0101 0111-0000-1010-0110
        // }
        CPPUNIT_ASSERT("float tolerance compare testC" &&
                       !real_util::floatToleranceEqual(a, b, real_util::compareMaskGen32(1)));
        CPPUNIT_ASSERT("float tolerance compare testD" &&
                       real_util::floatToleranceEqual(a, b, real_util::compareMaskGen32(2)));
    }
    {
        const double a = 1234567890.0;
        const double b = 1234567890.000001;
        /* for debug
        std::cerr << real_util::doubleDump(a) << '\n'
                  << real_util::doubleDump(b) << '\n';
        */
        // double dump 'a' {
        //   val:1.23457e+09
        //   hex:0x41d26580b4800000
        //   bit:0100-0001-1101-0010-0110-0101-1000-0000-1011-0100-1000-0000 0000-0000-0000-0000
        // }
        // double dump 'b' {
        //   val:1.23457e+09
        //   hex:0x41d26580b4800004
        //   bit:0100-0001-1101-0010-0110-0101-1000-0000-1011-0100-1000-0000 0000-0000-0000-0100
        // }
        CPPUNIT_ASSERT("double tolerance compare testA" &&
                       !real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(2)));
        CPPUNIT_ASSERT("double tolerance compare testB" &&
                       real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(3)));
    }
    {
        const double a = 78.9;
        const double b = 78.9000000000001;
        /* for debug
        std::cerr << real_util::doubleDump(a) << '\n'
                  << real_util::doubleDump(b) << '\n';
        */
        // double dump 'a' {
        //   val:78.9
        //   hex:0x4053b9999999999a
        //   bit:0100-0000-0101-0011-1011-1001-1001-1001-1001-1001-1001-1001 1001-1001-1001-1010
        // }
        // double dump 'b' {
        //   val:78.9
        //   hex:0x4053b999999999a1
        //   bit:0100-0000-0101-0011-1011-1001-1001-1001-1001-1001-1001-1001 1001-1001-1010-0001
        // }
        CPPUNIT_ASSERT("double tolerance compare testC" &&
                       !real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(2)));
        CPPUNIT_ASSERT("double tolerance compare testD" &&
                       real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(3)));
    }
    {
        const double a = -12345678.9;
        const double b = -12.3456789;
        /* for debug
        std::cerr << real_util::doubleDump(a) << '\n'
                  << real_util::doubleDump(b) << '\n';
        */
        // double dump 'a' {
        //   val:-1.23457e+07
        //   hex:0xc1678c29dccccccd
        //   bit:1100-0001-0110-0111-1000-1100-0010-1001-1101-1100-1100-1100 1100-1100-1100-1101
        // }
        // double dump 'b' {
        //   val:-12.3457
        //   hex:0xc028b0fcd324d5a2
        //   bit:1100-0000-0010-1000-1011-0000-1111-1100-1101-0011-0010-0100 1101-0101-1010-0010
        // }
        CPPUNIT_ASSERT("double tolerance compare testE" &&
                       !real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(56)));
        CPPUNIT_ASSERT("double tolerance compare testF" &&
                       real_util::doubleToleranceEqual(a, b, real_util::compareMaskGen64(57)));
    }

    TIME_END;
}

void
TestArg::testConstructor()
{
    TIME_START;

    {
        Arg arg;
        CPPUNIT_ASSERT("default constructor test" &&
                       arg.verify("", "", 0, 0,
                                  Arg::ArgTbl{},
                                  Arg::ArgTbl{}));
    }
    {
        Arg arg(" a01 b23\n \t c45  d67 \t# test  \n");
        CPPUNIT_ASSERT("constructed top level arg from command line test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a01", "b23", "c45", "d67"},
                                  Arg::ArgTbl{"", "a01", "b23", "c45", "d67", "#", "test"}));
    }
    {
        Arg arg("a\\#1.exr b");
        CPPUNIT_ASSERT("escaped '#' in a word test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a#1.exr", "b"},
                                  Arg::ArgTbl{"", "a#1.exr", "b"}));
    }
    {
        Arg arg("foo \\#ff0000 # comment");
        CPPUNIT_ASSERT("escaped '#' at the head of a word with comment test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"foo", "#ff0000"},
                                  Arg::ArgTbl{"", "foo", "#ff0000", "#", "comment"}));
    }
    {
        Arg arg("a#b c");
        CPPUNIT_ASSERT("not escaped '#' in a word starts comment test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a"},
                                  Arg::ArgTbl{"", "a", "#b", "c"}));
    }
    {
        Arg arg("a # b#c d\\#e");
        CPPUNIT_ASSERT("comment part is kept as is (no more split and escape) test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a"},
                                  Arg::ArgTbl{"", "a", "#", "b#c", "d\\#e"}));
    }
    {
        Arg arg("C:\\dir\\a.txt a\\ b\\");
        CPPUNIT_ASSERT("other backslash is literal test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"C:\\dir\\a.txt", "a\\", "b\\"},
                                  Arg::ArgTbl{"", "C:\\dir\\a.txt", "a\\", "b\\"}));
    }
    {
        Arg arg("a\\\\#b"); // 'a' '\' '\' '#' 'b' : 1st backslash is literal, 2nd one escapes '#'
        CPPUNIT_ASSERT("backslash before escaped '#' test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a\\#b"},
                                  Arg::ArgTbl{"", "a\\#b"}));
    }
    {
        Arg arg("\\# \\#\\#");
        CPPUNIT_ASSERT("escaped '#' only word test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"#", "##"},
                                  Arg::ArgTbl{"", "#", "##"}));
    }
    {
        Arg arg("a\tb\r\nc\r");
        CPPUNIT_ASSERT("CRLF and tab test" &&
                       arg.verify("", "", 0, 1,
                                  Arg::ArgTbl{"a", "b", "c"},
                                  Arg::ArgTbl{"", "a", "b", "c"}));
    }
    {
        Arg arg("opt", "a\\#1 b # c");
        CPPUNIT_ASSERT("escaped '#' by command-name w/ argument line test" &&
                       arg.verify("opt", "", 0, 2,
                                  Arg::ArgTbl{"a#1", "b"},
                                  Arg::ArgTbl{"", "opt", "a#1", "b", "#", "c"}));
    }
    {
        const std::vector<std::string> strTbl {"a#1.exr", "#", "##x", "a\\#b", "\\", "#\\", "plain"};
        for (const auto& str : strTbl) {
            Arg arg("cmd " + Arg::escapeComment(str) + " # comment");
            CPPUNIT_ASSERT("escapeComment round trip test" &&
                           arg.verify("", "", 0, 1,
                                      Arg::ArgTbl{"cmd", str},
                                      Arg::ArgTbl{"", "cmd", str, "#", "comment"}));
        }
        CPPUNIT_ASSERT("escapeComment test" && Arg::escapeComment("a#b#") == "a\\#b\\#");
        CPPUNIT_ASSERT("escapeComment no '#' test" && Arg::escapeComment("abc") == "abc");
    }
    {
        Arg arg0("optA", "optB a\\#1 b # c d");
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("childArg with escaped '#' test" &&
                       arg1.verify("optA optB", "", 0, 3,
                                   Arg::ArgTbl{"a#1", "b"},
                                   Arg::ArgTbl{"", "optA", "optB", "a#1", "b", "#", "c", "d"}));
    }
    {
        Arg arg0("abc", "a  b\tc# AA BB CC");
        Arg arg1 = arg0;
        CPPUNIT_ASSERT("construct by command-name w/ argument line and copy test" &&
                       arg1.verify("abc", "", 0, 2,
                                   Arg::ArgTbl{"a", "b", "c"},
                                   Arg::ArgTbl{"", "abc", "a", "b", "c", "#", "AA", "BB", "CC"}));
    }
    {
        auto setStrFromHeap = [](const std::string &str) -> char * {
            char *buf = (char *)malloc(str.size() + 1);
            memcpy(buf, str.data(), str.size() + 1); // copy with last null
            return buf;
        };

        char *av[3];
        av[0] = setStrFromHeap("A");
        av[1] = setStrFromHeap("B");
        av[2] = setStrFromHeap("C");
        Arg arg(3, av);
        CPPUNIT_ASSERT("construct by ac av test" &&
                       arg.verify("A", "", 0, 1,
                                  Arg::ArgTbl{"B", "C"},
                                  Arg::ArgTbl{"A", "B", "C"}));
        free(av[0]);
        free(av[1]);
        free(av[2]);
    }
    {
        Arg arg(0, nullptr); // argc == 0 must not crash
        CPPUNIT_ASSERT("construct by ac av with argc=0 test" &&
                       arg.verify("", "", 0, 0,
                                  Arg::ArgTbl{},
                                  Arg::ArgTbl{}));
    }
    {
        Arg arg0("optA", "optB a b c");
        // arg0++; // CPPCHECK returns error
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("arg++ and childArg test" &&
                       arg1.verify("optA optB", "", 0, 3,
                                  Arg::ArgTbl{"a", "b", "c"},
                                  Arg::ArgTbl{"", "optA", "optB", "a", "b", "c"}));
    }
    {
        Arg arg0("optA", "optB a b c");
        // arg0++; // CPPCHECK returns error
        arg0 += 1;
        Arg arg1 = arg0.childArg("optA(child)");
        CPPUNIT_ASSERT("arg++ and childArg test 2" &&
                       arg1.verify("optA(child)", "", 0, 3,
                                  Arg::ArgTbl{"a", "b", "c"},
                                  Arg::ArgTbl{"", "optA", "optB", "a", "b", "c"}));
    }
    {
        Arg arg0("optA", "optB a b # c d");
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("childArg with comment test" &&
                       arg1.verify("optA optB", "", 0, 3,
                                   Arg::ArgTbl{"a", "b"},
                                   Arg::ArgTbl{"", "optA", "optB", "a", "b", "#", "c", "d"}));
    }
    {
        Arg arg0("optA", "optB # c d");
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("childArg with comment only test" &&
                       arg1.verify("optA optB", "", 0, 3,
                                   Arg::ArgTbl{},
                                   Arg::ArgTbl{"", "optA", "optB", "#", "c", "d"}));
    }
    {
        Arg arg0("optA b c # d");
        ++arg0;
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("top level childArg with comment test" &&
                       arg1.verify("optA", "", 0, 2,
                                   Arg::ArgTbl{"b", "c"},
                                   Arg::ArgTbl{"", "optA", "b", "c", "#", "d"}));
        ++arg1;
        Arg arg2 = arg1.childArg();
        CPPUNIT_ASSERT("grandchild childArg with comment test" &&
                       arg2.verify("optA b", "", 0, 3,
                                   Arg::ArgTbl{"c"},
                                   Arg::ArgTbl{"", "optA", "b", "c", "#", "d"}));
    }
    {
        Arg arg0("optA", "optB a b");
        arg0.setCerrOutput(false);
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CerrCapture cap;
        arg1.msg("hello\n");
        CPPUNIT_ASSERT("childArg inherits mCerrOutput(false) test" && cap.str().empty());
    }
    {
        Arg arg0("optA", "optB a b");
        arg0 += 1;
        Arg arg1 = arg0.childArg();
        CerrCapture cap;
        arg1.msg("hello\n");
        CPPUNIT_ASSERT("childArg inherits mCerrOutput(true) test" && cap.str() == "hello\n");
    }
    {
        Arg arg0; // empty Arg must not crash on childArg
        Arg arg1 = arg0.childArg();
        CPPUNIT_ASSERT("childArg of empty Arg test" &&
                       arg1.verify("", "", 0, 0,
                                   Arg::ArgTbl{},
                                   Arg::ArgTbl{}));
    }

    TIME_END;
}

void
TestArg::testUtil()
{
    TIME_START;

    {
        std::string cmdLine("optA a b c d");
        Arg arg(cmdLine);
        std::string argCmdLine = arg.currArgCmdLine();
        CPPUNIT_ASSERT("currArgCmdLine test" && argCmdLine == cmdLine);
    }
    {
        // currArgCmdLine() must be re-parsable by Arg(cmdLine) without losing any words
        struct RoundTrip {
            std::string mCmdLine;
            Arg::ArgTbl mWords; // expected words
        };
        const std::vector<RoundTrip> roundTripTbl {
            {"file a\\#1.exr", {"file", "a#1.exr"}},   // escaped '#' in a word
            {"cmd \\#ff0000 x", {"cmd", "#ff0000", "x"}}, // escaped '#' at the head of a word
            {"p a\\\\#b", {"p", "a\\#b"}},             // backslash followed by escaped '#'
            {"a\\ b x\\", {"a\\", "b", "x\\"}},        // '\' not followed by '#' is literal
            {"\\# \\#\\#", {"#", "##"}},               // words which consist of '#' only
            {"optA a b # comment", {"optA", "a", "b"}} // comment is not included
        };
        for (const auto& itr : roundTripTbl) {
            Arg arg(itr.mCmdLine);
            const std::string argCmdLine = arg.currArgCmdLine();
            Arg arg2(argCmdLine);
            CPPUNIT_ASSERT("currArgCmdLine words test" && arg.currArg() == itr.mWords);
            CPPUNIT_ASSERT("currArgCmdLine round trip test" && arg2.currArg() == itr.mWords);
        }
    }
    {
        // childArg().currArgCmdLine() is used for forwarding the rest of the command to the other process
        Arg arg("cmd file a\\#1.exr");
        ++arg;
        Arg arg2(arg.childArg().currArgCmdLine());
        const Arg::ArgTbl expected {"file", "a#1.exr"};
        CPPUNIT_ASSERT("childArg currArgCmdLine round trip test" && arg2.currArg() == expected);
    }
    {
        // argc/argv version does not treat '#' specially
        char a0[] = "cmd";
        char a1[] = "a#1.exr";
        char* argv[] = {a0, a1};
        Arg arg(2, argv);
        Arg arg2(arg.currArgCmdLine());
        const Arg::ArgTbl expected {"a#1.exr"};
        CPPUNIT_ASSERT("argc/argv currArgCmdLine test" &&
                       arg.currArgCmdLine() == "a\\#1.exr" &&
                       arg2.currArg() == expected);
    }
    {
        Arg arg;
        CPPUNIT_ASSERT("empty test" && (arg.empty() && arg.emptyArg()));
    }
    {
        Arg arg("-h -H -help -HELP -Help ? -? - --");
        CPPUNIT_ASSERT("help test0" && arg.isHelp());
        CPPUNIT_ASSERT("help test1" && arg.isHelp());
        CPPUNIT_ASSERT("help test2" && arg.isHelp());
        CPPUNIT_ASSERT("help test3" && arg.isHelp());
        CPPUNIT_ASSERT("help test4" && arg.isHelp());
        CPPUNIT_ASSERT("help test5" && arg.isHelp());
        CPPUNIT_ASSERT("help test6" && arg.isHelp());
        CPPUNIT_ASSERT("help test7" && arg.isHelp());
        CPPUNIT_ASSERT("help test8" && arg.isHelp());
    }
    {
        Arg arg("-optA a b c");
        CPPUNIT_ASSERT("isOpt test" && arg.isOpt("optA"));
    }
    {
        Arg arg("-optA a b c");
        CPPUNIT_ASSERT("size test" && (arg.size() == 4));
    }

    TIME_END;
}

void
TestArg::testGetter()
{
    TIME_START;

    {
        Arg arg("optA 1 -23 4.56");
        CPPUNIT_ASSERT("operator() test" && (arg(2) == "-23"));
        CPPUNIT_ASSERT("argument id overrun test" &&
                       (idRangeTest(arg, 4) ==
                        "Argument id overrun id:4 {\n"
                        "   optA 1 -23 4.56\n"
                        "}                  ^^^"));
    }
    {
        Arg arg("optA true TRUE True t T on ON On 1 off");
        CPPUNIT_ASSERT("as<bool> test" &&
                       arg.as<bool>(1) &&
                       arg.as<bool>(2) &&
                       arg.as<bool>(3) &&
                       arg.as<bool>(4) &&
                       arg.as<bool>(5) &&
                       arg.as<bool>(6) &&
                       arg.as<bool>(7) &&
                       arg.as<bool>(8) &&
                       arg.as<bool>(9) &&
                       !arg.as<bool>(10));
    }
    {
        CPPUNIT_ASSERT("as<int> test" && asTest<int>());
        CPPUNIT_ASSERT("as<long> test" && asTest<long>());
        CPPUNIT_ASSERT("as<long long> test" && asTest<long long>());
        CPPUNIT_ASSERT("as<unsigned long> test" && asTest<unsigned long>());
        CPPUNIT_ASSERT("as<unsigned long long> test" && asTest<unsigned long long>());

        CPPUNIT_ASSERT("as<float> test" && asTestReal(1.234567f, 2));
        CPPUNIT_ASSERT("as<double> test" && asTestReal((double)1.234567, 2));
    }

    TIME_END;
}

void
TestArg::testArgShift()
{
    TIME_START;

    Arg argOrg("optA", "a b c");

    {
        Arg arg = argOrg;
        Arg argA = arg++;
        Arg argB = arg;
        CPPUNIT_ASSERT("arg++ testA" &&
                       argA.verify("optA", "", 0, 2,
                                   Arg::ArgTbl{"a", "b", "c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
        CPPUNIT_ASSERT("arg++ testB" &&
                       argB.verify("optA", "", 0, 3,
                                   Arg::ArgTbl{"b", "c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
    }
    {
        Arg arg = argOrg;
        Arg argA = arg;
        arg += 2;
        Arg argB = arg;
        CPPUNIT_ASSERT("arg += 2 testA" &&
                       argA.verify("optA", "", 0, 2,
                                   Arg::ArgTbl{"a", "b", "c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
        CPPUNIT_ASSERT("arg += 2 testB" &&
                       argB.verify("optA", "", 0, 4,
                                   Arg::ArgTbl{"c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
    }
    {
        Arg arg = argOrg;
        Arg argA = ++arg;
        Arg argB = arg;
        CPPUNIT_ASSERT("++arg testA" &&
                       argA.verify("optA", "", 0, 3,
                                   Arg::ArgTbl{"b", "c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
        CPPUNIT_ASSERT("++arg testB" &&
                       argB.verify("optA", "", 0, 3,
                                   Arg::ArgTbl{"b", "c"},
                                   Arg::ArgTbl{"", "optA", "a", "b", "c"}));
    }
    {
        Arg arg = argOrg;
        arg.shiftArgAll();
        CPPUNIT_ASSERT("shiftArgAll() test" &&
                       arg.verify("optA", "", 0, 5,
                                  Arg::ArgTbl{},
                                  Arg::ArgTbl{"", "optA", "a", "b", "c"}));
    }

    TIME_END;
}

} // namespace unittest
} // namespace grid_util
} // namespace scene_rdl2
