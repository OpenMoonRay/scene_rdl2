// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0
#include "Parser.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace scene_rdl2 {
namespace grid_util {

namespace {

std::string
cleanStr(const std::string& arg)
{
    std::string workStr = str_util::trimBlank(arg);
    workStr = str_util::replaceBlankToSingleSpace(workStr);
    return workStr;
}

std::string
showItemType(const ParserItem::ItemType& itemType)
{
    switch (itemType) {
    case ParserItem::ItemType::OPT : return "OPT";
    case ParserItem::ItemType::ARG : return "ARG";
    default : break;
    }
    return "?";
}

std::string
spaces(const size_t total)
{
    std::string out;
    for (size_t i = 0; i < total; ++i) out.push_back(' ');
    return out;
}

// std::isspace() and std::isblank() require unsigned char range value
bool
isSpaceChar(const char c)
{
    return std::isspace(static_cast<unsigned char>(c)) != 0;
}

bool
isBlankChar(const char c)
{
    return std::isblank(static_cast<unsigned char>(c)) != 0;
}

} // namespace

ParserItem::ParserItem(const ItemType itemType,
                       const std::string& name,
                       const std::string& argMsg,
                       const std::string& shortMsg,
                       ParserFunc parserFunc) // parser action function
    : mItemType(itemType)
    , mName(str_util::trimBlank(name))
    , mArgMsg(cleanStr(argMsg))
    , mShortMsg(shortMsg)
    , mParserFunc(std::move(parserFunc))
    , mArgCount(0)
{
    mArgCount = computeArgCount();
}

std::string
ParserItem::showShortMsgWithConstLen(const size_t offsetShortMsg,
                                     const size_t maxLen) const
{
    if (mShortMsg.empty()) return "";
    if (maxLen == 0) return mShortMsg;       // special case

    std::string output;
    auto outPartialShortMsg = [&](const size_t startId, const size_t endId) {
        if (!output.empty()) {
            output += '\n';
            output += std::string(offsetShortMsg, ' ');
        }
        std::string partial = mShortMsg.substr(startId, endId - startId + 1);
        const size_t lastNonSpace = partial.find_last_not_of(" \t\v\f\r\n");
        partial.erase((lastNonSpace == std::string::npos) ? 0 : lastNonSpace + 1); // rm trailing spaces
        output += partial;
    };
    auto isSplitWordAtLineEnd = [&](const size_t id) {
        if (id >= mShortMsg.size()) return false;
        if (isSpaceChar(mShortMsg[id])) return false;
        if (id + 1 < mShortMsg.size() && isSpaceChar(mShortMsg[id + 1])) return false;
        return true;
    };
    auto getNextStartId = [&](const size_t endId, size_t& newStartId) {
        for (size_t id = endId; id < mShortMsg.size(); ++id) {
            if (!isSpaceChar(mShortMsg[id])) {
                newStartId = id;
                return true;
            }
        }
        return false;
    };

    // Each line contains up to maxLen characters of the message. If a word is split at the end of the line,
    // '-' is added as the (maxLen + 1)th character of the line.
    size_t startId = 0;
    while (1) {
        const size_t endId = startId + maxLen - 1;
        outPartialShortMsg(startId, endId);

        if (mShortMsg.size() - 1 <= endId) {
            break; // end of short message
        }

        if (isSplitWordAtLineEnd(endId)) output += '-';
        if (!getNextStartId(endId + 1, startId)) {
            break; // end of short message
        }
    }

    return output;
}

std::string
ParserItem::show() const
{
    std::ostringstream ostr;
    ostr << "ParserItem {\n"
         << "  mItemType:" << showItemType(mItemType) << '\n'
         << "  mName:" << mName << '\n'
         << "  mArgMsg:" << mArgMsg << '\n'
         << "  mShortMsg:" << mShortMsg << '\n'
         << "  mArgCount:" << mArgCount << '\n'
         << "}";
    return ostr.str();
}

size_t
ParserItem::computeArgCount() const
{
    // The following operations are already applied to mArgMsg before calling this function:
    //  1) str_util::trimBlank()
    //  2) str_util::replaceBlankToSingleSpace()
    if (mArgMsg.empty()) return 0;

    size_t totalArg = 1;
    for (size_t i = 0; i < mArgMsg.size(); ++i) {
        if (isBlankChar(mArgMsg[i])) totalArg++;
    }
    return totalArg;
}

//------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------

bool
Parser::main(Arg& arg) const
{
    if (arg.noNeedToEvalTest(hasArgument())) return true;

    if (arg.isHelp()) {
        return arg.msg(usage(arg.comName(), true) + '\n');
    }

    try {
        size_t argId = 0;
        do {
            bool find = false;

            // option parameter
            for (const auto& itr: mParserItemTbl) {
                if (itr.isOpt() && arg.isOpt(itr.name())) {
                    if (itr.getArgCount() > arg.size()) {
                        throw(arg.warnMsgLastNext("option argument count error"));
                    }
                    arg.setCurrOptName(itr.name());
                    if (!itr(arg)) { // evaluate option
                        throw(arg.warnMsgEvalOpt("eval option error"));
                    }
                    find = true;
                }
            }

            // argument parameter
            if (!find) {
                size_t localArgId = 0;
                for (const auto& itr: mParserItemTbl) {
                    if (itr.isArg()) {
                        if (argId == localArgId) {
                            if (itr.getArgCount() > arg.size()) {
                                throw(arg.warnMsgLastNext("command argument count error"));
                            }
                            arg.setCurrArgId(argId);
                            if (!itr(arg)) { // evaluate argument
                                throw(arg.warnMsgEvalArg("eval argument error"));
                            }
                            argId += itr.getArgCount();
                            find = true;
                        } else {
                            localArgId += itr.getArgCount();
                        }
                    }
                }
            }

            if (!find) {
                if (mErrorUnknownOption) {
                    throw(arg.warnMsgCurrVal("Unknown option/argument"));
                } else {
                    break; // this is not an error
                }
            }
        } while (!arg.emptyArg());

        if (argId != mTotalArgCount) {
            arg.setCurrArgId(argId);
            throw(arg.warnMsgEvalArg("needs more argument"));
        }
    }
    catch (const std::string& error) {
        if (!mSilentEvalError) arg.msg(error + '\n');
        return false;
    }
    catch (const std::invalid_argument& e) {
        if (!mSilentEvalError) {
            arg.msg(arg.warnMsgPrevVal("invalid argument") + ' ' + e.what() + " failed\n");
        }
        return false;
    }
    catch (const std::out_of_range& e) {
        if (!mSilentEvalError) {
            arg.msg(arg.warnMsgPrevVal("out of range") + ' ' + e.what() + " failed\n");
        }
        return false;
    }
    catch (const std::exception& e) {
        if (!mSilentEvalError) {
            arg.msg(arg.warnMsgPrevVal("exception") + ' ' + e.what() + " failed\n");
        }
        return false;
    }
    catch (...) {
        if (!mSilentEvalError) arg.msg("unknown error\n");
        return false;
    }

    return true;
}

bool
Parser::main(const std::string& singleCommandLine, std::string& outputMessage) const
{
    outputMessage.clear();

    Arg tmpArg(singleCommandLine);
    tmpArg.setMessageHandler([&](const std::string& msg) -> bool {
        if (!outputMessage.empty()) outputMessage += '\n';
        outputMessage += msg;
        // We want to remove last '\n'
        if (!outputMessage.empty() && outputMessage.back() == '\n') outputMessage.pop_back();
        return true;
    });
    tmpArg.setCerrOutput(false);

    const bool flag = main(tmpArg);

    outputMessage = str_util::rmLastNL(outputMessage);

    return flag;
}

bool
Parser::mainCmdFile(const std::string& cmdFilename,
                    const bool stopAtError,
                    std::string& outputMessage) const
{
    std::vector<std::string> cmdTbl;

    std::ifstream infile(cmdFilename);
    if (!infile) {
        std::ostringstream ostr;
        ostr << "Cannot open file:" << cmdFilename;
        outputMessage = ostr.str();
        return false; // error
    }
    std::string currLine;
    while (std::getline(infile, currLine)) {
        cmdTbl.push_back(currLine);
    }
    if (!infile.eof()) {
        // The loop above ended by a read failure (e.g. the path is a directory or an I/O error happened).
        // This is not a normal end of file and no command is evaluated.
        outputMessage = "Cannot read file:" + cmdFilename;
        return false; // error
    }
    infile.close();

    //------------------------------

    outputMessage.clear();
    if (cmdTbl.empty()) return true; // empty

    auto addOutputMsg = [&](const std::string& msg) {
        if (msg.empty()) return;
        if (!outputMessage.empty()) outputMessage += '\n';
        outputMessage += msg;
    };
    auto showCmdFile = [&](const size_t errorLineId) -> std::string {
        std::ostringstream ostr;
        for (size_t lineId = 0; lineId < cmdTbl.size(); ++lineId) {
            ostr << "lineId:" << lineId << ' ' << cmdTbl[lineId];
            if (lineId == errorLineId) ostr << " # error command line\n";
            else ostr << '\n';
        }
        return ostr.str();
    };

    bool allOk = true;
    for (size_t lineId = 0; lineId < cmdTbl.size(); ++lineId) {
        const std::string& currCmd = cmdTbl[lineId];

        // skip blank line and comment only line
        const std::string trimmedCmd = str_util::trimBlank(currCmd);
        if (trimmedCmd.empty() || trimmedCmd[0] == '#') continue;

        std::string currOutputMsg;
        if (!main(currCmd, currOutputMsg)) {
            if (stopAtError) {
                std::ostringstream ostr;
                ostr << "Parser::main() FAILED. file:" << cmdFilename << " lineId:" << lineId << " {\n"
                     << "  data={\n"
                     << str_util::addIndent(str_util::rmLastNL(showCmdFile(lineId)), 2) << '\n'
                     << "  }\n"
                     << "  err={\n"
                     << str_util::addIndent(str_util::rmLastNL(currOutputMsg), 2) << '\n'
                     << "  }\n"
                     << "}";
                addOutputMsg(ostr.str());
                return false; // error
            }
            allOk = false; // keep going but remember the failure
        }
        addOutputMsg(currOutputMsg);
    }
    return allOk;
}

std::string
Parser::show() const
{
    std::ostringstream ostr;
    ostr << "Parser {\n"
         << "  mDescription:" << mDescription << '\n'
         << str_util::addIndent(showParserItemTbl()) << '\n'
         << "}";
    return ostr.str();
}

//------------------------------------------------------------------------------------------

std::string
Parser::usage(const std::string& comName, const bool sort) const
{
    std::ostringstream ostr;

    auto newLineIfNeed = [&]() -> std::string { return ostr.str().size() ? "\n" : ""; };
    auto usageTop = [&]() {
        ostr << "[Usage] : " << comName;
        if (hasOptions()) {
            ostr << " [options]";
        }
        if (itemCount(ParserItem::ItemType::ARG)) {
            ostr << argListOneLine();
        }
    };

    if (!comName.empty()) usageTop();

    if (!mDescription.empty()) {
        ostr << newLineIfNeed() << "[Description] : " << mDescription;
    }
    if (hasArgument()) {
        ostr << newLineIfNeed() << "[Argument]\n" << str_util::addIndent(argListDetail());
    }
    if (hasOptions()) {
        ostr << newLineIfNeed()
             << (comName.empty() ? "[Command]" : "[Options]") << '\n'
             << str_util::addIndent(optList(sort));
    }

    return ostr.str();
}

std::string
Parser::argListOneLine() const
{
    std::ostringstream ostr;
    for (const auto& itr: mParserItemTbl) {
        if (itr.isArg()) ostr << " " << itr.argMsg();
    }
    return ostr.str();
}

std::string
Parser::argListDetail() const
{
    std::vector<const ParserItem*> argTbl;
    size_t maxArgMsgLen = 0;
    for (const auto& itr: mParserItemTbl) {
        if (itr.isArg()) {
            argTbl.push_back(&itr);
            maxArgMsgLen = std::max(maxArgMsgLen, itr.getArgMsgLen());
        }
    }

    std::ostringstream ostr;
    for (size_t i = 0; i < argTbl.size(); ++i) {
        const ParserItem& currItem = *argTbl[i];
        ostr << currItem.argMsg() << spaces(maxArgMsgLen - currItem.getArgMsgLen());
        ostr << " : " << currItem.shortMsg();
        if (i != argTbl.size() - 1) ostr << '\n';
    }

    return ostr.str();
}

std::string
Parser::optList(const bool sort) const
{
    std::vector<const ParserItem*> optTbl;
    size_t maxNameLen = 0;
    size_t maxArgMsgLen = 0;
    for (const auto& itr: mParserItemTbl) {
        if (itr.isOpt()) {
            optTbl.push_back(&itr);
            maxNameLen = std::max(maxNameLen, itr.getNameLen());
            maxArgMsgLen = std::max(maxArgMsgLen, itr.getArgMsgLen());
        }
    }
    if (sort) {
        std::sort(optTbl.begin(), optTbl.end(),
                  [](const ParserItem* a, const ParserItem* b) {
                      return a->name() < b->name();
                  });
    }

    const size_t offsetShortMsg = (maxNameLen + maxArgMsgLen +
                                   (maxArgMsgLen ? 1 : 0) /* space between name and arguments */ +
                                   3 /* space between arguments and shortMessage */);

    constexpr size_t totalMaxLen = 110; // 110 column max
    constexpr size_t indentLen = 2; // one indentation (i.e. = 2 spaces) added by str_util::addIndent()
    constexpr size_t minimumShortMsgLen = 10;
    size_t shortMsgMaxLen = 0;
    if (offsetShortMsg + indentLen + minimumShortMsgLen <= totalMaxLen) {
        // Compute the length of max shortMessage. If shortMessage is more than
        // this limitation, output as multiple lines.
        shortMsgMaxLen = totalMaxLen - indentLen - offsetShortMsg;
    } else {
        // We give up multiple line output and simply output whole shortMessage as single line
    }
    std::ostringstream ostr;
    for (size_t i = 0; i < optTbl.size(); ++i) {
        const ParserItem& currItem = *optTbl[i];
        ostr << spaces(maxNameLen - currItem.getNameLen()) << currItem.name();
        if (maxArgMsgLen) ostr << ' ';
        ostr << currItem.argMsg() << spaces(maxArgMsgLen - currItem.getArgMsgLen());
        ostr << " : " << currItem.showShortMsgWithConstLen(offsetShortMsg, shortMsgMaxLen);
        if (i != optTbl.size() - 1) ostr << '\n';
    }

    return ostr.str();
}

size_t
Parser::itemCount(const ParserItem::ItemType itemType) const
{
    size_t count = 0;
    for (const auto& itr: mParserItemTbl) {
        if (itr.getItemType() == itemType) count++;
    }
    return count;
}

size_t
Parser::totalArgCount() const
{
    size_t count = 0;
    for (const auto& itr: mParserItemTbl) {
        if (itr.getItemType() == ParserItem::ItemType::ARG) {
            count += itr.getArgCount();
        }
    }
    return count;
}

std::string
Parser::showParserItemTbl() const
{
    std::ostringstream ostr;
    ostr << "mParserItemTbl (size:" << mParserItemTbl.size() << ") {\n";
    for (size_t i = 0; i < mParserItemTbl.size(); ++i) {
        ostr << str_util::addIndent("id:" + std::to_string(i) + ' ' + mParserItemTbl[i].show()) << '\n';
    }
    ostr << "}";
    return ostr.str();
}

} // namespace grid_util
} // namespace scene_rdl2
