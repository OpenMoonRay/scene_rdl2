// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0


#pragma once

// Include this before any other includes!
#include <scene_rdl2/common/platform/Platform.h>

#include "SceneClass.h"
#include "SceneContext.h"
#include "SceneObject.h"
#include "Shader.h"
#include "Types.h"

#include <scene_rdl2/common/except/exceptions.h>
#include <scene_rdl2/common/math/Color.h>
#include <scene_rdl2/render/logging/logging.h>

#include <string>

namespace scene_rdl2 { namespace shading { class State; } }

namespace scene_rdl2 {
namespace rdl2 {

class Map : public Shader
{
public:
    typedef Shader Parent;

    Map(const SceneClass& sceneClass, const std::string& name);
    virtual ~Map();
    static SceneObjectInterface declare(SceneClass& sceneClass);

    AttributeType getOutputType() { return mOutputType; }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        math::Color* result) const
    {
        MNRY_ASSERT(mSampleFunc != nullptr);
        mSampleFunc(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Bool* result) const
    {
        MNRY_ASSERT(mSampleFuncBool != nullptr);
        mSampleFuncBool(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Int* result) const
    {
        MNRY_ASSERT(mSampleFuncInt != nullptr);
        mSampleFuncInt(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Vec4f* result) const
    {
        MNRY_ASSERT(mSampleFuncVec4f != nullptr);
        mSampleFuncVec4f(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Rgba* result) const
    {
        MNRY_ASSERT(mSampleFuncRgba != nullptr);
        mSampleFuncRgba(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Mat3f* result) const
    {
        MNRY_ASSERT(mSampleFuncMat3f != nullptr);
        mSampleFuncMat3f(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        Mat4f* result) const
    {
        MNRY_ASSERT(mSampleFuncMat4f != nullptr);
        mSampleFuncMat4f(this, tls, state, result);
    }

    finline void sample(moonray::shading::TLState *tls,
                        const moonray::shading::State& state,
                        SceneObject** result) const
    {
        MNRY_ASSERT(mSampleFuncSceneObject != nullptr);
        mSampleFuncSceneObject(this, tls, state, result);
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Colorv* resultv) const
    {
        if (mSampleFuncv != nullptr) {
            mSampleFuncv(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         Boolv* resultv) const
    {
        if (mSampleFuncvBool != nullptr) {
            mSampleFuncvBool(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Intv* resultv) const
    {
        if (mSampleFuncvInt != nullptr) {
            mSampleFuncvInt(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Vec4fv* resultv) const
    {
        if (mSampleFuncvVec4f != nullptr) {
            mSampleFuncvVec4f(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Rgbav* resultv) const
    {
        if (mSampleFuncvRgba != nullptr) {
            mSampleFuncvRgba(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Mat3fv* resultv) const
    {
        if (mSampleFuncvMat3f != nullptr) {
            mSampleFuncvMat3f(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::Mat4fv* resultv) const
    {
        if (mSampleFuncvMat4f != nullptr) {
            mSampleFuncvMat4f(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    finline void samplev(moonray::shading::TLState *tls,
                         const rdl2::Statev * statev,
                         rdl2::SceneObject** resultv) const
    {
        if (mSampleFuncvSceneObject != nullptr) {
            mSampleFuncvSceneObject(this, tls, statev, resultv, util::sAllOnMask);
        }
    }

    public:
    // Unfortunately, this member has been made public to allow
    //  for computing its offset into the binary
    union {
        SampleFunc mSampleFunc;
        SampleFuncBool mSampleFuncBool;
        SampleFuncInt mSampleFuncInt;
        SampleFuncVec4f mSampleFuncVec4f;
        SampleFuncRgba mSampleFuncRgba;
        SampleFuncMat3f mSampleFuncMat3f;
        SampleFuncMat4f mSampleFuncMat4f;
        SampleFuncSceneObject mSampleFuncSceneObject;
    };

    union {
        SampleFuncv mSampleFuncv;
        SampleFuncvBool mSampleFuncvBool;
        SampleFuncvInt mSampleFuncvInt;
        SampleFuncvVec4f mSampleFuncvVec4f;
        SampleFuncvRgba mSampleFuncvRgba;
        SampleFuncvMat3f mSampleFuncvMat3f;
        SampleFuncvMat4f mSampleFuncvMat4f;
        SampleFuncvSceneObject mSampleFuncvSceneObject;
    };

    // Save away mSampleFunc when we fatal for future restore
    union {
        SampleFunc mOriginalSampleFunc;
        SampleFuncBool mOriginalSampleFuncBool;
        SampleFuncInt mOriginalSampleFuncInt;
        SampleFuncVec4f mOriginalSampleFuncVec4f;
        SampleFuncRgba mOriginalSampleFuncRgba;
        SampleFuncMat3f mOriginalSampleFuncMat3f;
        SampleFuncMat4f mOriginalSampleFuncMat4f;
        SampleFuncSceneObject mOriginalSampleFuncSceneObject;
    };
    union {
        SampleFuncv mOriginalSampleFuncv;
        SampleFuncvBool mOriginalSampleFuncvBool;
        SampleFuncvInt mOriginalSampleFuncvInt;
        SampleFuncvVec4f mOriginalSampleFuncvVec4f;
        SampleFuncvRgba mOriginalSampleFuncvRgba;
        SampleFuncvMat3f mOriginalSampleFuncvMat3f;
        SampleFuncvMat4f mOriginalSampleFuncvMat4f;
        SampleFuncvSceneObject mOriginalSampleFuncvSceneObject;
    };


    // Not thread safe!
    virtual void setFataled(bool fataled) {
        if (fataled && (mOriginalSampleFuncvBool == nullptr)) {
            switch (mOutputType) {
              case TYPE_BOOL:
                  mOriginalSampleFuncBool = mSampleFuncBool;
                  mOriginalSampleFuncvBool = mSampleFuncvBool;
                  mSampleFuncBool = mSceneClass.getSceneContext()->getFatalSampleFuncBool();
                  mSampleFuncvBool = nullptr;
                  break;
              case TYPE_INT:
                  mOriginalSampleFuncInt = mSampleFuncInt;
                  mOriginalSampleFuncvInt = mSampleFuncvInt;
                  mSampleFuncInt = mSceneClass.getSceneContext()->getFatalSampleFuncInt();
                  mSampleFuncvInt = nullptr;
                  break;
              case TYPE_VEC4F:
                  mOriginalSampleFuncVec4f = mSampleFuncVec4f;
                  mOriginalSampleFuncvVec4f = mSampleFuncvVec4f;
                  mSampleFuncVec4f = mSceneClass.getSceneContext()->getFatalSampleFuncVec4f();
                  mSampleFuncvVec4f = nullptr;
                  break;
              case TYPE_RGB:
                  mOriginalSampleFunc = mSampleFunc;
                  mOriginalSampleFuncv = mSampleFuncv;
                  mSampleFunc = mSceneClass.getSceneContext()->getFatalSampleFunc();
                  mSampleFuncv = nullptr;
                  break;
              case TYPE_RGBA:
                  mOriginalSampleFuncRgba = mSampleFuncRgba;
                  mOriginalSampleFuncvRgba = mSampleFuncvRgba;
                  mSampleFuncRgba = mSceneClass.getSceneContext()->getFatalSampleFuncRgba();
                  mSampleFuncvRgba = nullptr;
                  break;
              case TYPE_MAT3F:
                  mOriginalSampleFuncMat3f = mSampleFuncMat3f;
                  mOriginalSampleFuncvMat3f = mSampleFuncvMat3f;
                  mSampleFuncMat3f = mSceneClass.getSceneContext()->getFatalSampleFuncMat3f();
                  mSampleFuncvMat3f = nullptr;
                  break;
              case TYPE_MAT4F:
                  mOriginalSampleFuncMat4f = mSampleFuncMat4f;
                  mOriginalSampleFuncvMat4f = mSampleFuncvMat4f;
                  mSampleFuncMat4f = mSceneClass.getSceneContext()->getFatalSampleFuncMat4f();
                  mSampleFuncvMat4f = nullptr;
                  break;
              default:
                  break;
            }
        } else if (!fataled) {
            // If we're no longer fataled and we stored away
            // a sample func, restore it.
            if (mOriginalSampleFuncBool != nullptr) {
                mSampleFuncBool = mOriginalSampleFuncBool;
                mOriginalSampleFuncBool = nullptr;
            }
            if (mOriginalSampleFuncvBool != nullptr) {
                mSampleFuncvBool = mOriginalSampleFuncvBool;
                mOriginalSampleFuncvBool = nullptr;
            }
        }
    }

    // Some maps can be used as an extra aov map.
    virtual bool getIsExtraAovMap(String &label, Bool &postScatter) const;

    // If this is a ListMap, this method will return true and
    // fill out the vector of map objects
    virtual bool getIsListMap(std::vector<const Map *> &mapList) const;


protected:
    AttributeType mOutputType;
    char padding[4]; // padding to make sure derived classes start with 8 byte alignment
};

template <>
inline const Map*
SceneObject::asA() const
{
    return isA<Map>() ? static_cast<const Map*>(this) : nullptr;
}

template <>
inline Map*
SceneObject::asA()
{
    return isA<Map>() ? static_cast<Map*>(this) : nullptr;
}

} // namespace rdl2
} // namespace scene_rdl2

