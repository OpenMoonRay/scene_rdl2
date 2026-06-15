// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0


#include "Map.h"

#include "SceneClass.h"
#include "Types.h"

#include <string>

namespace scene_rdl2 {
namespace rdl2 {

Map::Map(const SceneClass& sceneClass, const std::string& name) :
    Parent(sceneClass, name)
{
    // it doesn't matter which union member we initialize to nullptr
    // since the pointers are all the same size
    mSampleFuncBool = nullptr;
    mSampleFuncvBool = nullptr;
    mOutputType = TYPE_RGB; // this should be overwritten in the constructor of the derived class
    mOriginalSampleFuncBool = nullptr;
    mOriginalSampleFuncvBool = nullptr;
    // Add the Map interface.
    mType |= INTERFACE_MAP;
}

Map::~Map()
{
}

bool
Map::getIsExtraAovMap(String &label, Bool &postScatter) const
{
    return false;
}

bool
Map::getIsListMap(std::vector<const Map *> &mapList) const
{
    return false;
}

SceneObjectInterface
Map::declare(SceneClass& sceneClass)
{
    auto interface = Parent::declare(sceneClass);

    return interface | INTERFACE_MAP;
}

} // namespace rdl2
} // namespace scene_rdl2

