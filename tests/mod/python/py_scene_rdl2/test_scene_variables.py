# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""SceneVariables. There is no C++ test file for this class;
TestSceneContext::testSceneVariables is mirrored in test_scene_context.py."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, make_context, requires_test_dsos


class TestSceneVariables(Rdl2TestCase):

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        self.scene_vars = self.context.getSceneVariables()

    def test_is_scene_object(self):
        self.assertIsInstance(self.scene_vars, scene_rdl2.SceneObject)
        self.assertEqual(self.scene_vars.getName(), "__SceneVariables__")

    def test_resolution(self):
        self.assertEqual(self.scene_vars.get("image_width"), 1920)
        self.scene_vars.set("image_width", 640)
        self.scene_vars.set("image_height", 480)
        self.assertEqual(self.scene_vars.getRezedWidth(), 640)
        self.scene_vars.set("res", 2.0)
        self.assertEqual(self.scene_vars.getRezedWidth(), 320)
        self.assertEqual(self.scene_vars.getRezedHeight(), 240)

    def test_machines(self):
        self.assertEqual(self.scene_vars.getMachineId(), 0)
        self.assertEqual(self.scene_vars.getNumMachines(), 1)

    def test_debug_pixel(self):
        self.scene_vars.set("debug_pixel", [10, 20])
        self.assertEqual(self.scene_vars.get("debug_pixel").toList(), [10, 20])
        self.assertEqual(self.scene_vars.getDebugPixel().toList(), [10, 20])

    # TODO: fix SceneVariables.getDebugPixel and getSubViewport
    # (py_scene_rdl2_scene_variables.cc): getDebugPixel drops the "is set" bool
    # and returns an uninitialized Vec2i when unset; getSubViewport raises
    # "No to_python (by-value) converter found for C++ type:
    # scene_rdl2::math::HalfOpenViewport" and has the same unset problem.
    # def test_sub_viewport(self):
    #     self.scene_vars.set("sub_viewport", [0, 0, 9, 19])
    #     viewport = self.scene_vars.getSubViewport()
    #     self.assertIsNotNone(viewport)

    @requires_test_dsos
    def test_camera(self):
        context = make_context(proxy_mode=True)
        scene_vars = context.getSceneVariables()
        camera = context.createSceneObject("LibLadenCamera", "camera")
        scene_vars.set("camera", camera)
        self.assertEqual(scene_vars.get("camera").getName(), "camera")
        self.assertEqual(context.getPrimaryCamera().getName(), "camera")

        not_a_camera = context.createSceneObject("UserData", "data")
        with self.assertRaises(RuntimeError):
            scene_vars.set("camera", not_a_camera)


if __name__ == "__main__":
    unittest.main()
