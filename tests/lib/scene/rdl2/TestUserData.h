// Copyright 2023-2024 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0

/// @file TestUserData.h

#pragma once

#include <scene_rdl2/scene/rdl2/UserData.h>
#include <cppunit/TestFixture.h>
#include <cppunit/extensions/HelperMacros.h>

#include <memory>

namespace scene_rdl2 {
namespace rdl2 {

class SceneContext;

namespace unittest {

class TestUserData: public CppUnit::TestFixture
{
public:
    void setUp() override;
    void tearDown() override;

    void testSetup();
    void testAscii();
    void testBinary();
    void testReleaseData();
    void testReleasedUpdateThrows();
    void testReleasedWriteThrows();

    CPPUNIT_TEST_SUITE(TestUserData);
    CPPUNIT_TEST(testSetup);
    CPPUNIT_TEST(testAscii);
    CPPUNIT_TEST(testBinary);
    CPPUNIT_TEST(testReleaseData);
    CPPUNIT_TEST(testReleasedUpdateThrows);
    CPPUNIT_TEST(testReleasedWriteThrows);
    CPPUNIT_TEST_SUITE_END();

private:
    void compare(SceneContext const &a, SceneContext const &b) const;

    std::unique_ptr<SceneContext> mContext;
    std::string mUserDataName;

    String mBoolKey;
    BoolVector mBoolValues;
    String mIntKey;
    IntVector mIntValues;
    String mFloatKey;
    FloatVector mFloatValues;
    String mStringKey;
    StringVector mStringValues;
    String mColorKey;
    RgbVector mColorValues;
    String mVec2fKey;
    Vec2fVector mVec2fValues;
    String mVec3fKey;
    Vec3fVector mVec3fValues;
    String mVec4fKey;
    Vec4fVector mVec4fValues0;
    Vec4fVector mVec4fValues1;
    String mMat4fKey;
    Mat4fVector mMat4fValues;
};

} // namespace unittest
} // namespace rdl2
} // namespace scene_rdl2

