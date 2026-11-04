// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <scene_rdl2/common/grid_util/Parser.h>

#include <cppunit/extensions/HelperMacros.h>
#include <cppunit/TestFixture.h>

namespace scene_rdl2 {
namespace grid_util {
namespace unittest {

class TestParser : public CppUnit::TestFixture
{
public:
    void setUp() {}
    void tearDown() {}

    void testParserOpt();
    void testParserArg();
    void testParserOptArg();
    void testParserCmdFile();
    void testParserCmdFileDirectory();
    void testParserCmdFileEmpty();
    void testParserReset();
    void testParserHelpWrap();
    void testParserSilentEvalError();
    void testParserEscapedHash();

    CPPUNIT_TEST_SUITE(TestParser);
    CPPUNIT_TEST(testParserOpt);
    CPPUNIT_TEST(testParserArg);
    CPPUNIT_TEST(testParserOptArg);
    CPPUNIT_TEST(testParserCmdFile);
    CPPUNIT_TEST(testParserCmdFileDirectory);
    CPPUNIT_TEST(testParserCmdFileEmpty);
    CPPUNIT_TEST(testParserReset);
    CPPUNIT_TEST(testParserHelpWrap);
    CPPUNIT_TEST(testParserSilentEvalError);
    CPPUNIT_TEST(testParserEscapedHash);
    CPPUNIT_TEST_SUITE_END();

protected:
    struct InOutData {
        std::string mTestName;
        std::string mInput;
        std::string mOutput;
    };

    Parser parserConfigure(bool setOpt, bool setArg, bool errUnknownOpt = true) const;
    bool verifyParser(const Parser& parser,
                      const std::string& cmdLine,
                      const std::string& target,
                      bool showOut = false) const;
    std::string runParser(const Parser& parser,
                          const std::string& cmdLine,
                          bool showOut = false) const;
    bool verifyParserCmdFile(const Parser& parser,
                             const std::vector<InOutData>& inOutData) const;
    bool createCmdFile(const std::string& filename,
                       const std::vector<InOutData>& inOutData) const;
    std::string showCmdFile(const std::string& filename) const;
    void rmCmdFile(const std::string& cmdFilename) const;
    std::string genTmpCmdFilename() const;
    bool verifyCmdFileSkipLines() const;
    bool verifyCmdFileStopAtError() const;
    bool verifyCmdFileOpenError() const;

    std::vector<InOutData> genInOutDataParserOpt() const;
    std::vector<InOutData> genInOutDataParserArg() const;
    std::vector<InOutData> genInOutDataParserOptArg() const;
};

} // namespace unittest
} // namespace grid_util
} // namespace scene_rdl2
