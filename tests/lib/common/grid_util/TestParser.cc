// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#include "TestParser.h"
#include "TimeOutput.h"

#include <algorithm>
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <unistd.h> // getpid

namespace scene_rdl2 {
namespace grid_util {
namespace unittest {

void
TestParser::testParserOpt()
{
    TIME_START;

    CPPUNIT_ASSERT("empty opt definition" &&
                   verifyParser(parserConfigure(false, false), "foo 1.23 4.56",
                                "WARNING : Unknown option/argument {\n"
                                "   foo 1.23 4.56\n"
                                "}  ^^^\n"
                                "main():false"));
    CPPUNIT_ASSERT("unknown opt no-error mode" &&
                   verifyParser(parserConfigure(true, false, false), "baz qux quux corge",
                                "main():true"));

    const std::vector<InOutData> data = genInOutDataParserOpt();
    for (size_t i = 0; i < data.size(); ++i) {
        const bool flag = verifyParser(parserConfigure(true, false), data[i].mInput, data[i].mOutput);
        if (!flag) {
            std::cerr << "ERROR : testParserOpt() i:" << i << " testName:" << data[i].mTestName << " FAILED!\n";
        }
        CPPUNIT_ASSERT("testParserOpt()" && flag);
    }

    TIME_END;
}

void
TestParser::testParserArg()
{
    TIME_START;

    CPPUNIT_ASSERT("missing all arguments only opt" &&
                   verifyParser(parserConfigure(true, false), "",
                                "main():true"));

    const std::vector<InOutData> data = genInOutDataParserArg();
    for (size_t i = 0; i < data.size(); ++i) {
        const bool flag = verifyParser(parserConfigure(false, true), data[i].mInput, data[i].mOutput);
        if (!flag) {
            std::cerr << "ERROR : testParserArg() i:" << i << " testName:" << data[i].mTestName << " FAILED!\n";
        }
        CPPUNIT_ASSERT("testParserArg()" && flag);
    }

    TIME_END;
}

void
TestParser::testParserOptArg()
{
    TIME_START;

    const std::vector<InOutData> data = genInOutDataParserOptArg();
    for (size_t i = 0; i < data.size(); ++i) {
        const bool flag = verifyParser(parserConfigure(true, true), data[i].mInput, data[i].mOutput);
        if (!flag) {
            std::cerr << "ERROR : testParserOptArg() i:" << i << " testName:" << data[i].mTestName << " FAILED!\n";
        }
        CPPUNIT_ASSERT("testParserOptArg()" && flag);
    }

    TIME_END;
}

void
TestParser::testParserCmdFile()
{
    TIME_START;

    CPPUNIT_ASSERT("cmdFile opt" &&
                   verifyParserCmdFile(parserConfigure(true, false), genInOutDataParserOpt()));
    CPPUNIT_ASSERT("cmdFile arg" &&
                   verifyParserCmdFile(parserConfigure(false, true), genInOutDataParserArg()));
    CPPUNIT_ASSERT("cmdFile opt and arg" &&
                   verifyParserCmdFile(parserConfigure(true, true), genInOutDataParserOptArg()));

    CPPUNIT_ASSERT("cmdFile skip blank and comment lines" && verifyCmdFileSkipLines());
    CPPUNIT_ASSERT("cmdFile stopAtError" && verifyCmdFileStopAtError());
    CPPUNIT_ASSERT("cmdFile open error" && verifyCmdFileOpenError());

    TIME_END;
}

void
TestParser::testParserCmdFileDirectory()
{
    TIME_START;

    const Parser parser = parserConfigure(true, false);
    const std::string dirName = std::filesystem::temp_directory_path().string();

    for (const bool stopAtError : {true, false}) {
        std::string outputMsg;
        const bool flag = parser.mainCmdFile(dirName, stopAtError, outputMsg);

        // Directory input may fail either when opening or when reading.
        const std::string openError = "Cannot open file:" + dirName;
        const std::string readError = "Cannot read file:" + dirName;

        std::ostringstream diagnostic;
        diagnostic << "Directory input must be rejected"
                   << " path:{" << dirName << '}'
                   << " stopAtError:" << std::boolalpha << stopAtError
                   << " actualResult:" << flag
                   << " actualMessage:{" << outputMsg << '}'
                   << " expectedResult:false"
                   << " expectedMessage:{" << openError
                   << "} or {" << readError << '}';

        CPPUNIT_ASSERT_MESSAGE(
            diagnostic.str(),
            !flag && (outputMsg == openError || outputMsg == readError));
    }

    TIME_END;
}

void
TestParser::testParserCmdFileEmpty()
{
    TIME_START;

    const Parser parser = parserConfigure(true, false);
    const std::string cmdFilename = genTmpCmdFilename();

    {
        std::ofstream outfile(cmdFilename);
        if (!outfile) {
            rmCmdFile(cmdFilename);
            CPPUNIT_FAIL("Cannot create empty command file:" + cmdFilename);
        }

        outfile.close();
        if (!outfile) {
            rmCmdFile(cmdFilename);
            CPPUNIT_FAIL("Cannot close empty command file:" + cmdFilename);
        }
    }

    for (const bool stopAtError : {true, false}) {
        std::string outputMsg = "previous output";
        const bool flag = parser.mainCmdFile(cmdFilename, stopAtError, outputMsg);

        if (!flag || !outputMsg.empty()) {
            rmCmdFile(cmdFilename);

            std::ostringstream diagnostic;
            diagnostic << "Empty command file must succeed and clear output"
                       << " path:{" << cmdFilename << '}'
                       << " stopAtError:" << std::boolalpha << stopAtError
                       << " actualResult:" << flag
                       << " actualMessage:{" << outputMsg << '}'
                       << " expectedResult:true expectedMessage:{}";

            CPPUNIT_FAIL(diagnostic.str());
        }
    }

    rmCmdFile(cmdFilename);

    TIME_END;
}

void
TestParser::testParserReset()
{
    TIME_START;

    Parser parser = parserConfigure(false, true); // mTotalArgCount becomes 3
    parser.reset();
    parser.opt("baz", "<a>", "option baz",
               [&](Arg& arg) -> bool {
                   arg.msg(std::string("baz a:") + arg(0) + '\n');
                   arg += 1;
                   return true;
               });
    // stale mTotalArgCount would cause "needs more argument" error here
    CPPUNIT_ASSERT("reset() clears argument count" &&
                   verifyParser(parser, "baz 1", "baz a:1\nmain():true"));

    TIME_END;
}

void
TestParser::testParserEscapedHash()
{
    TIME_START;

    Parser parser;
    parser.opt("file", "<name>", "set file name",
               [](Arg& arg) -> bool {
                   arg.msg("file:" + arg(0) + '\n');
                   arg += 1;
                   return true;
               });
    CPPUNIT_ASSERT("escaped '#' file name" &&
                   verifyParser(parser, "file a\\#1.exr # comment", "file:a#1.exr\nmain():true"));
    CPPUNIT_ASSERT("not escaped '#' is comment" &&
                   verifyParser(parser, "file a#1.exr", "file:a\nmain():true"));
    CPPUNIT_ASSERT("escapeComment() and parser" &&
                   verifyParser(parser, "file " + Arg::escapeComment("/tmp/#1/a#.exr"),
                                "file:/tmp/#1/a#.exr\nmain():true"));

    TIME_END;
}

void
TestParser::testParserSilentEvalError()
{
    TIME_START;

    auto configure = [](const bool silent) {
        Parser parser;
        parser.setSilentEvalError(silent);
        parser.opt("evalFail", "", "return false",
                   [](Arg&) -> bool { return false; });
        parser.opt("toInt", "<a>", "convert to int",
                   [](Arg& arg) -> bool { return arg.as<int>(0) >= 0; }); // might throw invalid_argument
        parser.opt("outRange", "<a>", "out of range",
                   [](Arg& arg) -> bool { return arg.as<int>(0) >= 0; }); // might throw out_of_range
        parser.opt("stdExcept", "", "throw std::exception",
                   [](Arg&) -> bool { throw std::runtime_error("test"); });
        parser.opt("unknownExcept", "", "throw unknown type",
                   [](Arg&) -> bool { throw 123; });
        parser.opt("msgFail", "", "output message and return false",
                   [](Arg& arg) -> bool { arg.msg("action message\n"); return false; });
        return parser;
    };

    const Parser silentParser = configure(true);
    CPPUNIT_ASSERT("silent: eval error" && verifyParser(silentParser, "evalFail", "main():false"));
    CPPUNIT_ASSERT("silent: unknown option" && verifyParser(silentParser, "unknownOpt", "main():false"));
    CPPUNIT_ASSERT("silent: argument count error" && verifyParser(silentParser, "toInt", "main():false"));
    CPPUNIT_ASSERT("silent: invalid_argument" && verifyParser(silentParser, "toInt abc", "main():false"));
    CPPUNIT_ASSERT("silent: out_of_range" &&
                   verifyParser(silentParser, "outRange 99999999999999999999", "main():false"));
    CPPUNIT_ASSERT("silent: std::exception" && verifyParser(silentParser, "stdExcept", "main():false"));
    CPPUNIT_ASSERT("silent: unknown exception" && verifyParser(silentParser, "unknownExcept", "main():false"));
    CPPUNIT_ASSERT("silent: action's own message is kept" &&
                   verifyParser(silentParser, "msgFail", "action message\nmain():false"));

    const Parser normalParser = configure(false);
    CPPUNIT_ASSERT("normal: invalid_argument has message" &&
                   runParser(normalParser, "toInt abc").find("invalid argument") != std::string::npos);
    CPPUNIT_ASSERT("normal: out_of_range has message" &&
                   runParser(normalParser, "outRange 99999999999999999999").find("out of range") !=
                   std::string::npos);
    CPPUNIT_ASSERT("normal: std::exception has message" &&
                   runParser(normalParser, "stdExcept").find("exception") != std::string::npos);
    CPPUNIT_ASSERT("normal: unknown exception has message" &&
                   runParser(normalParser, "unknownExcept").find("unknown error") != std::string::npos);
    CPPUNIT_ASSERT("normal: eval error has message" &&
                   runParser(normalParser, "evalFail").find("eval option error") != std::string::npos);

    TIME_END;
}

void
TestParser::testParserHelpWrap()
{
    TIME_START;

    auto wrap = [](const std::string& msg, const size_t offset, const size_t maxLen) {
        ParserItem item(ParserItem::ItemType::OPT, "x", "", msg,
                        [](Arg&) -> bool { return true; });
        return item.showShortMsgWithConstLen(offset, maxLen);
    };

    CPPUNIT_ASSERT("empty message" && wrap("", 0, 10) == "");
    CPPUNIT_ASSERT("maxLen=0 returns whole message" && wrap("abc def ghi", 0, 0) == "abc def ghi");
    CPPUNIT_ASSERT("shorter than maxLen" && wrap("short", 3, 10) == "short");
    CPPUNIT_ASSERT("exactly maxLen" && wrap("abcdefghij", 3, 10) == "abcdefghij");
    CPPUNIT_ASSERT("trailing spaces are removed" && wrap("abc   ", 0, 10) == "abc");

    // word split : '-' is placed at (maxLen + 1)th
    CPPUNIT_ASSERT("maxLen+1 chars single word" && wrap("abcdefghijk", 0, 10) == "abcdefghij-\nk");
    CPPUNIT_ASSERT("long single word with offset" &&
                   wrap("abcdefghijklmnopqrstuvwxyz", 3, 10) == "abcdefghij-\n   klmnopqrst-\n   uvwxyz");

    // word end is just at maxLen : no '-'
    CPPUNIT_ASSERT("word end at maxLen" && wrap("abcdefghij klm", 0, 10) == "abcdefghij\nklm");

    // wrap at a blank : no '-' and no trailing space
    CPPUNIT_ASSERT("wrap at blank" &&
                   wrap("aaaa bbbb cccc dddd eeee ffff gggg hhhh", 0, 10) ==
                   "aaaa bbbb\ncccc dddd\neeee ffff\ngggg hhhh");
    CPPUNIT_ASSERT("wrap at multiple blanks" && wrap("aaaa bbbb   cccc", 2, 10) == "aaaa bbbb\n  cccc");

    // Total column check of the help message. 110 columns max and '-' goes to the 111th column.
    {
        Parser parser;
        parser.opt("foo", "<a>", std::string(300, 'x'), [](Arg&) -> bool { return true; });
        const std::string help = runParser(parser, "help");

        std::istringstream istr(help);
        std::string line;
        size_t maxLineLen = 0;
        bool foundHyphenAtLast = false;
        while (std::getline(istr, line)) {
            maxLineLen = std::max(maxLineLen, line.size());
            if (line.size() == 111 && line.back() == '-') foundHyphenAtLast = true;
        }
        CPPUNIT_ASSERT("help line length max" && maxLineLen == 111);
        CPPUNIT_ASSERT("help wrap '-' at 111th column" && foundHyphenAtLast);
    }

    // All options have no argument message. Wrapped lines should be aligned with the first line.
    {
        Parser parser;
        parser.opt("foo", "", std::string(300, 'x'), [](Arg&) -> bool { return true; });
        const std::string help = runParser(parser, "help");

        std::istringstream istr(help);
        std::string line;
        size_t maxLineLen = 0;
        size_t firstMsgPos = std::string::npos;
        bool aligned = true;
        while (std::getline(istr, line)) {
            maxLineLen = std::max(maxLineLen, line.size());
            const size_t pos = line.find(" : ");
            if (pos != std::string::npos) {
                firstMsgPos = pos + 3;
            } else if (firstMsgPos != std::string::npos && !line.empty() && line[0] == ' ') {
                // continuation line
                if (line.find_first_not_of(' ') != firstMsgPos) aligned = false;
            }
        }
        CPPUNIT_ASSERT("help no argMsg line length max" && maxLineLen == 111);
        CPPUNIT_ASSERT("help no argMsg continuation lines are aligned" &&
                       firstMsgPos != std::string::npos && aligned);
    }

    TIME_END;
}

//-----------------------------------------------------------------------------------------

bool
TestParser::verifyCmdFileSkipLines() const
{
    // Parser which has argument definitions fails with an empty command line.
    // But blank lines and comment only lines in the command file must be skipped.
    const Parser parser = parserConfigure(true, true);
    const std::string cmdFilename = genTmpCmdFilename();
    {
        std::ofstream outfile(cmdFilename);
        if (!outfile) return false;
        outfile << "\n"
                << "   \t \n"
                << "# comment only\n"
                << "   # indented comment\n"
                << "foo 1.23 4.56 1 2 3 # trailing comment\n"
                << "\n";
    }
    std::string outputMsg;
    const bool flag = parser.mainCmdFile(cmdFilename, true, outputMsg);
    rmCmdFile(cmdFilename);
    if (!flag) std::cerr << "verifyCmdFileSkipLines " << outputMsg << '\n';
    return flag;
}

bool
TestParser::verifyCmdFileStopAtError() const
{
    const Parser parser = parserConfigure(true, false);
    const std::string cmdFilename = genTmpCmdFilename();
    {
        std::ofstream outfile(cmdFilename);
        if (!outfile) return false;
        outfile << "foo 1.23 4.56\n"
                << "baz qux\n" // unknown option -> error
                << "bar 7.89\n";
    }
    std::string outputMsg;
    const bool flag = parser.mainCmdFile(cmdFilename, true, outputMsg);
    rmCmdFile(cmdFilename);

    if (flag) return false; // should fail
    if (outputMsg.find("lineId:1") == std::string::npos) return false; // error line id
    if (outputMsg.find("bar c:7.89") != std::string::npos) return false; // must stop at error line
    return true;
}

bool
TestParser::verifyCmdFileOpenError() const
{
    const Parser parser = parserConfigure(true, false);
    std::string outputMsg;
    const bool flag = parser.mainCmdFile("/nonexistent-dir/nonexistent.cmd", true, outputMsg);
    return !flag && outputMsg.find("Cannot open file") != std::string::npos;
}

Parser
TestParser::parserConfigure(const bool setOpt, const bool setArg, const bool errUnknownOpt) const
{
    Parser parser;

    if (setOpt) {
        parser.opt("foo", "<a> <b>", "option foo",
                   [&](Arg& arg) -> bool {
                       arg.msg(std::string("foo a:") + arg(0) + " b:" + arg(1) + '\n');
                       arg += 2;
                       return true;
                   });
        parser.opt("bar", "<c>", "option bar",
                   [&](Arg& arg) -> bool {
                       std::string argC = (arg++)(0);
                       arg.msg(std::string("bar c:") + argC + '\n');
                       return (std::stoi(argC) >= 0.0) ? true : false;
                   });
    }

    if (setArg) {
        parser.arg("<A> <B>", "2 args",
                   [&](Arg& arg) -> bool {
                       arg.msg(std::string("A:") + arg(0) + " B:" + arg(1) + '\n');
                       arg += 2;
                       return true;
                   });
        parser.arg("<C>", "1 arg",
                   [&](Arg& arg) -> bool {
                       arg.msg(std::string("C:") + (arg++)(0) + '\n');
                       return true;
                   });
    }

    parser.setErrorUnknownOption(errUnknownOpt);

    return parser;
}

bool
TestParser::verifyParser(const Parser& parser,
                         const std::string& cmdLine,
                         const std::string& target,
                         const bool showOut) const
{
    return (runParser(parser, cmdLine, showOut) == target);
}

std::string
TestParser::runParser(const Parser& parser, const std::string& cmdLine, const bool showOut) const
{
    // construct arg based on the input cmdLine
    Arg arg(cmdLine);

    // setup message handler to the arg in order to keep all output into string
    std::string out;
    arg.setMessageHandler([&](const std::string& msg) -> bool {
            if (!out.empty() && out.back() != '\n') out += '\n';
            out += msg;
            return true;
        });
    arg.setCerrOutput(false); // disable printout to cerr

    const bool flag = parser.main(arg); // parser command line

    if (!out.empty() && out.back() != '\n') out += '\n';
    if (flag) {
        out += "main():true";
    } else {
        out += "main():false";
    }

    if (showOut) { // for debug
        std::ostringstream ostr;
        ostr << "out:{";
        for (size_t i = 0; i < out.size(); ++i) {
            if (out[i] == '\n') ostr << "\\n\n";
            else ostr << out[i];
        }
        ostr << "}:out";
        std::cerr << ostr.str() << '\n';
    }

    return out;
}

bool
TestParser::verifyParserCmdFile(const Parser& parser,
                                const std::vector<InOutData>& inOutData) const
{
    std::string cmdFilename = genTmpCmdFilename();
    if (!createCmdFile(cmdFilename, inOutData)) {
        rmCmdFile(cmdFilename);
        return false;
    }
    std::cerr << showCmdFile(cmdFilename) << '\n';

    // mainCmdFile() skips blank lines and comment only lines.
    auto isSkippedLine = [](const std::string& line) -> bool {
        const std::string trimmed = str_util::trimBlank(line);
        return trimmed.empty() || trimmed[0] == '#';
    };

    // mainCmdFile() returns false if any evaluated line failed even when stopAtError = false.
    bool expectedFlag = true;
    for (const auto& itr : inOutData) {
        if (isSkippedLine(itr.mInput)) continue;
        const std::string failTail = "main():false";
        if (itr.mOutput.size() >= failTail.size() &&
            itr.mOutput.compare(itr.mOutput.size() - failTail.size(), failTail.size(), failTail) == 0) {
            expectedFlag = false;
        }
    }

    std::string outputMsg;
    const bool flag = parser.mainCmdFile(cmdFilename,
                                         false, // stopAtError
                                         outputMsg);
    if (flag != expectedFlag) {
        std::cerr << "verifyParserCmdFile mainCmdFile() unexpected return value:"
                  << (flag ? "true" : "false") << '\n'
                  << outputMsg << '\n';
        rmCmdFile(cmdFilename);
        return false;
    }

    //------------------------------

    auto rmLastLine = [](const std::string& str) -> std::string {
        if (str.empty()) return "";
        std::string out = str;
        size_t pos = out.find_last_of('\n');
        if (pos != std::string::npos) out.erase(pos);
        else out.clear();
        return out;
    };

    auto showStr = [](const std::string& msg, const std::string& str) {
        std::ostringstream ostr;
        ostr << msg << " {\n"
             << str_util::addIndent(str) << '\n'
             << "}";
        return ostr.str();
    };

    std::string targetMsg;
    for (const auto& itr : inOutData) {
        if (isSkippedLine(itr.mInput)) continue;
        if (!targetMsg.empty()) targetMsg += '\n';
        // We only need to compare the parser execution output.
        // So, we need to remove the last line of mOutput.
        targetMsg += rmLastLine(itr.mOutput);
    }
    if (outputMsg != targetMsg) {
        std::ostringstream ostr;
        ostr << "ERROR verifyParserCmdFile {\n"
             << str_util::addIndent(showCmdFile(cmdFilename)) << '\n'
             << str_util::addIndent(showStr("outputMsg", outputMsg)) << '\n'
             << str_util::addIndent(showStr("targetMsg", targetMsg)) << '\n'
             << "}";
        std::cerr << ostr.str() << '\n';
        rmCmdFile(cmdFilename);
        return false;
    }

    rmCmdFile(cmdFilename);

    return true;
}

bool
TestParser::createCmdFile(const std::string& filename,
                          const std::vector<InOutData>& inOutData) const
{
    std::ofstream outfile(filename);
    if (!outfile) return false;

    for (size_t i = 0; i < inOutData.size(); ++i) {
        outfile << inOutData[i].mInput << '\n';
    }
    outfile.close();

    return true;
}

std::string
TestParser::showCmdFile(const std::string& cmdFilename) const
{
    std::ifstream infile(cmdFilename);
    if (!infile) return "";

    std::ostringstream ostr;
    ostr << "cmdFilename:" << cmdFilename << " {\n";
    std::string currLine;
    while (std::getline(infile, currLine)) {
        ostr << "  " << currLine << '\n';
    }
    ostr << "}";
    infile.close();

    return ostr.str();
}

void
TestParser::rmCmdFile(const std::string& filename) const
{
    std::error_code err;
    std::filesystem::remove(filename, err);
}

std::string
TestParser::genTmpCmdFilename() const
{
    // pid and counter make the filename unique even if multiple test processes run at the same time
    static std::atomic<unsigned> counter {0};
    const std::string name = "parserTest-" + std::to_string(::getpid()) + '-' +
        std::to_string(counter++) + ".cmd";
    return (std::filesystem::temp_directory_path() / name).string();
}

std::vector<TestParser::InOutData>
TestParser::genInOutDataParserOpt() const
{
    return std::vector<InOutData> {
        {
            "option help",
            "help",
            "[Command]\n"
            "  bar <c>     : option bar\n"
            "  foo <a> <b> : option foo\n"
            "main():true"
        },
        {
            "single opt",
            "foo 1.23 4.56",
            "foo a:1.23 b:4.56\n"
            "main():true"
        },
        {
            "single opt test2",
            "-foo 1.23 4.56",
            "foo a:1.23 b:4.56\n"
            "main():true"
        },
        {
            "single opt test3",
            "bar 7.89",
            "bar c:7.89\n"
            "main():true"
        },
        {
            "single opt test4 fail test",
            "bar -7.89",
            "bar c:-7.89\n"
            "eval option error optName:bar\n"
            "main():false"
        },
        {
            "full opt",
            "foo 1.23 4.56 bar 7.89",
            "foo a:1.23 b:4.56\n"
            "bar c:7.89\n"
            "main():true"
        },
        {
            "unknown opt",
            "baz qux quux corge",
            "WARNING : Unknown option/argument {\n"
            "   baz qux quux corge\n"
            "}  ^^^\n"
            "main():false"
        }
    };
}

std::vector<TestParser::InOutData>
TestParser::genInOutDataParserArg() const
{
    return std::vector<InOutData> {
        {
            "argument help",
            "help",
            "[Argument]\n"
            "  <A> <B> : 2 args\n"
            "  <C>     : 1 arg\n"
            "main():true"
        },
        {
            "full arg",
            "A B C",
            "A:A B:B\n"
            "C:C\n"
            "main():true"
        },
        {
            "missing all arguments with arg",
            "",
            "WARNING : command argument count error {\n"
            "  \n"
            "}  ^^^\n"
            "main():false"
        },
        {
            "missing one of arguments",
            "A",
            "WARNING : command argument count error {\n"
            "   A\n"
            "}    ^^^\n"
            "main():false"
        },
        {
            "too many arguments",
            "A B C D",
            "A:A B:B\n"
            "C:C\n"
            "WARNING : Unknown option/argument {\n"
            "   A B C D\n"
            "}        ^\n"
            "main():false"
        }
    };
}

std::vector<TestParser::InOutData>
TestParser::genInOutDataParserOptArg() const
{
    return std::vector<InOutData> {
        {
            "option + argument help",
            "help",
            "[Argument]\n"
            "  <A> <B> : 2 args\n"
            "  <C>     : 1 arg\n"
            "[Command]\n"
            "  bar <c>     : option bar\n"
            "  foo <a> <b> : option foo\n"
            "main():true"
        },
        {
            "full opt & full args",
            "bar 7.89 A0 B0 foo 1.23 4.56 C0",
            "bar c:7.89\n"
            "A:A0 B:B0\n"
            "foo a:1.23 b:4.56\n"
            "C:C0\n"
            "main():true"
        },
        {
            "missing all argument (partial opt + no arg)",
            "bar 7.89",
            "bar c:7.89\n"
            "needs more argument argId:0\n"
            "main():false"
        },
        {
            "missing one of arguments (partial opt + partial arg)",
            "bar 7.89 A B",
            "bar c:7.89\n"
            "A:A B:B\n"
            "needs more argument argId:2\n"
            "main():false"
        },
        {
            "too many argument w/ partial option",
            "bar 7.89 A B C D",
            "bar c:7.89\n"
            "A:A B:B\n"
            "C:C\n"
            "WARNING : Unknown option/argument {\n"
            "   bar 7.89 A B C D\n"
            "}                 ^\n"
            "main():false"
        },
    };
}

} // namespace unittest
} // namespace grid_util
} // namespace scene_rdl2
