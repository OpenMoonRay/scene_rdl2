# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestUserData. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, read_scene, write_scene


class TestUserData(Rdl2TestCase):

    MAT4F_VALUES = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
                    1, 3, 5, 7, 2, 4, 6, 8, 3, 5, 7, 9, 4, 6, 8, 0]

    DATA = [
        ("Bool", "test_bool_var", [True, False, True]),
        ("Int", "test_int_var", [1, 2, 3]),
        ("Float", "test_float_var", [4.0, 5.0, 6.0, 7.0]),
        ("String", "test_string_var", ["foo", "bar"]),
        ("Color", "test_color_var", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        ("Vec2f", "test_vec2f_var", [[1, 3], [5, 7]]),
        ("Vec3f", "test_vec3f_var", [[2, 4, 6], [8, 10, 12], [14, 16, 18]]),
    ]
    TYPES = {"Color": scene_rdl2.Rgb, "Vec2f": scene_rdl2.Vec2f, "Vec3f": scene_rdl2.Vec3f}

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        self.user_data = self.context.createSceneObject("UserData", "/testUserData").toUserData()

    def populate(self):
        """The values TestUserData::setUp sets."""
        for kind, key, values in self.DATA:
            self.assertFalse(getattr(self.user_data, "has%sData" % kind)())
            if kind in self.TYPES:
                values = [self.TYPES[kind](*v) for v in values]
            getattr(self.user_data, "set%sData" % kind)(key, values)
        self.assertFalse(self.user_data.hasMat4fData())
        # setMat4fData takes flat lists; see the TODO below for Mat4f objects.
        self.user_data.setMat4fData("test_mat4f_var", self.MAT4F_VALUES)

    def check(self, context):
        user_data = context.getSceneObject("/testUserData").toUserData()
        for kind, key, values in self.DATA:
            with self.subTest(kind):
                self.assertTrue(getattr(user_data, "has%sData" % kind)())
                self.assertEqual(getattr(user_data, "get%sKey" % kind)(), key)
                self.assertValuesEqual(getattr(user_data, "get%sValues" % kind)(), values)
        self.assertTrue(user_data.hasMat4fData())
        self.assertEqual(user_data.getMat4fKey(), "test_mat4f_var")
        self.assertValuesEqual(
            user_data.getMat4fValues(),
            [[self.MAT4F_VALUES[m + r * 4:m + r * 4 + 4] for r in range(4)] for m in (0, 16)])

    def round_trip(self, filename):
        self.populate()
        path = self.temp_path(filename)
        write_scene(self.context, path)
        result = scene_rdl2.SceneContext()
        read_scene(result, path)
        self.check(result)

    def test_setup(self):
        # Mirrors TestUserData::testSetup.
        # Omits: calling set*Data inside an update (see the TODO below).
        self.populate()
        self.check(self.context)

    # TODO: fix the UserData set*Data bindings (py_scene_rdl2_userdata.cc):
    # like SceneObject.set(), each opens its own UpdateGuard, so batching them
    # between beginUpdate() and endUpdate() -- as TestUserData's setUp does --
    # aborts the interpreter.
    # def test_set_data_inside_explicit_update(self):
    #     # Mirrors TestUserData::testSetup (the remainder).
    #     user_data = self.context.createSceneObject("UserData", "/batched").toUserData()
    #     user_data.beginUpdate()
    #     user_data.setIntData("ints", [1, 2])
    #     user_data.setFloatData("floats", [0.5])
    #     user_data.endUpdate()
    #     self.assertEqual(user_data.getIntValues().toList(), [1, 2])
    #     self.assertEqual(user_data.getFloatValues().toList(), [0.5])

    def test_ascii(self):
        # Mirrors TestUserData::testAscii.
        self.round_trip("UserData.rdla")

    def test_binary(self):
        # Mirrors TestUserData::testBinary.
        self.round_trip("UserData.rdlb")

    def test_color_from_lists(self):
        self.user_data.setColorData("color", [[1, 0.5, 0]])
        self.assertValuesAlmostEqual(self.user_data.getColorValues(), [[1, 0.5, 0]])

    # TODO: fix UserData.setMat4fData (py_scene_rdl2_userdata.cc): unlike the
    # other set*Data methods it rejects a list of Mat4f objects ("list/tuple
    # size is not divisible by T::N").
    # def test_mat4f_data(self):
    #     identity = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    #     self.user_data.setMat4fData("xform", [scene_rdl2.Mat4f(identity)])
    #     self.assertTrue(self.user_data.hasMat4fData())
    #     self.assertEqual(self.user_data.getMat4fKey(), "xform")
    #     self.assertValuesAlmostEqual(self.user_data.getMat4fValues(), [identity])


if __name__ == "__main__":
    unittest.main()
