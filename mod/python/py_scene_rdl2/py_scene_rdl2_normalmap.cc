// Copyright 2023-2026 DreamWorks Animation LLC
// SPDX-License-Identifier: Apache-2.0

#include "boost_python.h"
#include "py_scene_rdl2.h"

// scene_rdl2
#include <scene_rdl2/scene/rdl2/NormalMap.h>
using namespace scene_rdl2;

namespace py_scene_rdl2
{
    //------------------------------------
    // rdl2::NormalMap
    //------------------------------------

    void
    registerNormalMapPyBinding()
    {
        bp::class_<rdl2::NormalMap,
                   std::shared_ptr<rdl2::NormalMap>,
                   bp::bases<rdl2::RootShader>,
                   boost::noncopyable>("NormalMap", bp::no_init)

            .def(bp::init<const rdl2::SceneClass&, const std::string&>( (bp::arg("sceneClass"), bp::arg("name")) ))

            .def("declare",
                 &rdl2::NormalMap::declare,
                 bp::arg("sceneClass"))
            .staticmethod("declare");
    }

} // namespace py_scene_rdl2

