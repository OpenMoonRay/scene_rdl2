# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""The math value types and the std::vector container types. These do not mirror
C++ TestTypes, which covers string conversion and has no Python binding."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase

IDENTITY4 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
RAMP4 = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]


class TestVectors(Rdl2TestCase):

    VEC_TYPES = {
        "Vec2f": ("x", "y"), "Vec2d": ("x", "y"),
        "Vec3f": ("x", "y", "z"), "Vec3d": ("x", "y", "z"),
        "Vec4f": ("x", "y", "z", "w"), "Vec4d": ("x", "y", "z", "w"),
    }

    def test_default_is_zero(self):
        for name, fields in self.VEC_TYPES.items():
            with self.subTest(name):
                self.assertEqual(getattr(scene_rdl2, name)().toList(),
                                 [0.0] * len(fields))

    def test_component_constructor_and_accessors(self):
        for name, fields in self.VEC_TYPES.items():
            with self.subTest(name):
                values = [1.5 * (i + 1) for i in range(len(fields))]
                v = getattr(scene_rdl2, name)(*values)
                self.assertEqual([getattr(v, f) for f in fields], values)
                self.assertEqual([v[i] for i in range(len(fields))], values)
                self.assertEqual(v.toList(), values)

    def test_scalar_constructor_fills_all_components(self):
        self.assertEqual(scene_rdl2.Vec3f(2).toList(), [2.0, 2.0, 2.0])

    def test_list_constructor(self):
        self.assertEqual(scene_rdl2.Vec3f([1, 2, 3]).toList(), [1.0, 2.0, 3.0])

    def test_component_assignment(self):
        v = scene_rdl2.Vec3d()
        v.x = 5
        v.z = -1
        self.assertEqual(v.toList(), [5.0, 0.0, -1.0])

    def test_equality(self):
        self.assertTrue(scene_rdl2.Vec3d(1, 2, 3) == scene_rdl2.Vec3d(1, 2, 3))
        self.assertTrue(scene_rdl2.Vec3d(1, 2, 3) != scene_rdl2.Vec3d(1, 2, 4))

    def test_str(self):
        self.assertEqual(str(scene_rdl2.Vec3f(1, 2, 3)), "[ 1, 2, 3 ]")

    def test_length_and_normalize(self):
        v = scene_rdl2.Vec3f(3, 4, 0)
        self.assertAlmostEqual(v.length(), 5.0)
        self.assertAlmostEqual(v.lengthSqr(), 25.0)
        self.assertValuesAlmostEqual(v.normalize(), [0.6, 0.8, 0.0])

    def test_vec2i(self):
        v = scene_rdl2.Vec2i(3, -4)
        self.assertEqual((v.x, v.y), (3, -4))
        self.assertEqual(v.toList(), [3, -4])

    # TODO: fix the Vec2i binding (py_scene_rdl2_types.cc): it does not bind
    # __eq__/__ne__, so == falls back to identity and equal values compare False.
    # def test_vec2i_equality(self):
    #     self.assertTrue(scene_rdl2.Vec2i(1, 2) == scene_rdl2.Vec2i(1, 2))
    #     self.assertTrue(scene_rdl2.Vec2i(1, 2) != scene_rdl2.Vec2i(1, 3))


class TestColors(Rdl2TestCase):

    def test_rgb(self):
        c = scene_rdl2.Rgb(0.25, 0.5, 0.75)
        self.assertEqual((c.r, c.g, c.b), (0.25, 0.5, 0.75))
        self.assertEqual([c[0], c[1], c[2]], [0.25, 0.5, 0.75])
        self.assertEqual(c.toList(), [0.25, 0.5, 0.75])
        self.assertEqual(scene_rdl2.Rgb().toList(), [0.0, 0.0, 0.0])

    def test_rgba(self):
        c = scene_rdl2.Rgba(0.25, 0.5, 0.75, 1.0)
        self.assertEqual((c.r, c.g, c.b, c.a), (0.25, 0.5, 0.75, 1.0))
        self.assertEqual(c.toList(), [0.25, 0.5, 0.75, 1.0])

    def test_equality(self):
        self.assertTrue(scene_rdl2.Rgb(1, 2, 3) == scene_rdl2.Rgb(1, 2, 3))
        self.assertTrue(scene_rdl2.Rgb(1, 2, 3) != scene_rdl2.Rgb(1, 2, 4))


class TestMatrices(Rdl2TestCase):

    def test_default_is_zero(self):
        self.assertEqual(scene_rdl2.Mat4f().toList(), [[0.0] * 4] * 4)
        self.assertEqual(scene_rdl2.Mat3d().toList(), [[0.0] * 3] * 3)

    def test_row_list_constructor(self):
        for cls in (scene_rdl2.Mat4f, scene_rdl2.Mat4d):
            with self.subTest(cls.__name__):
                self.assertEqual(cls(RAMP4).toList(), RAMP4)
                # A tuple of rows must hold tuples; a list of rows must hold lists.
                self.assertEqual(cls(tuple(tuple(row) for row in RAMP4)).toList(), RAMP4)

    def test_constructor_rejects_flat_or_short_lists(self):
        with self.assertRaises(RuntimeError):
            scene_rdl2.Mat4f(list(range(16)))
        with self.assertRaises(RuntimeError):
            scene_rdl2.Mat4f([[1, 2, 3, 4]] * 3)

    def test_row_vector_constructor(self):
        rows = [scene_rdl2.Vec4f(*row) for row in RAMP4]
        self.assertEqual(scene_rdl2.Mat4f(*rows).toList(), RAMP4)

    # TODO: fix the Mat4d binding (py_scene_rdl2_types.cc): its four-row
    # constructor is bound with Vec4f rows, so Mat4d(Vec4d, ...) raises
    # ArgumentError.
    # def test_mat4d_row_vector_constructor_takes_vec4d(self):
    #     rows = [scene_rdl2.Vec4d(*row) for row in RAMP4]
    #     self.assertEqual(scene_rdl2.Mat4d(*rows).toList(), RAMP4)

    def test_row_accessors_and_flat_indexing(self):
        m = scene_rdl2.Mat4f(RAMP4)
        self.assertEqual(m.vx.toList(), RAMP4[0])
        self.assertEqual(m.vw.toList(), RAMP4[3])
        self.assertEqual(m[5], 5.0)
        with self.assertRaises(IndexError):
            m[16]

    def test_equality(self):
        self.assertTrue(scene_rdl2.Mat4f(RAMP4) == scene_rdl2.Mat4f(RAMP4))
        self.assertFalse(scene_rdl2.Mat4f(RAMP4) == scene_rdl2.Mat4f(IDENTITY4))

    def test_det_inverse_transpose(self):
        m = scene_rdl2.Mat4d([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]])
        self.assertAlmostEqual(m.det(), 16.0)
        self.assertValuesAlmostEqual(
            m.inverse(),
            [[0.5, 0, 0, 0], [0, 0.5, 0, 0], [0, 0, 0.5, 0], [0, 0, 0, 0.5]])
        self.assertEqual(scene_rdl2.Mat4f(RAMP4).transposed().toList(),
                         [list(col) for col in zip(*RAMP4)])

    def test_translate(self):
        m = scene_rdl2.Mat4f.translate(scene_rdl2.Vec4f(1, 2, 3, 1))
        self.assertEqual(m.toList(), IDENTITY4[:3] + [[1, 2, 3, 1]])

    def test_mat3(self):
        m = scene_rdl2.Mat3d([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
        self.assertAlmostEqual(m.det(), 6.0)
        self.assertEqual(scene_rdl2.Mat3f([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).vx.toList(),
                         [1, 2, 3])


class TestXform(Rdl2TestCase):

    def test_default(self):
        x = scene_rdl2.Xform3f()
        self.assertEqual(x.p.toList(), [0.0, 0.0, 0.0])

    def test_translate(self):
        x = scene_rdl2.Xform3f.translate(scene_rdl2.Vec3f(1, 2, 3))
        self.assertEqual(x.p.toList(), [1.0, 2.0, 3.0])
        self.assertEqual(x.l.vx.toList(), [1.0, 0.0, 0.0])

    def test_scale(self):
        x = scene_rdl2.Xform3f.scale(scene_rdl2.Vec3f(2, 3, 4))
        self.assertEqual(x.p.toList(), [0.0, 0.0, 0.0])
        self.assertEqual(x.l.vz.toList(), [0.0, 0.0, 4.0])


class TestContainers(Rdl2TestCase):

    def test_primitive_vectors(self):
        cases = {
            "BoolVector": [True, False],
            "IntVector": [1, -2],
            "LongVector": [2 ** 40, 7],
            "FloatVector": [0.5, 1.5],
            "DoubleVector": [0.25],
            "StringVector": ["a", "b"],
        }
        for name, values in cases.items():
            with self.subTest(name):
                self.assertEqual(getattr(scene_rdl2, name)(values).toList(), values)
                self.assertEqual(getattr(scene_rdl2, name)().toList(), [])

    def test_math_vectors(self):
        # Container type -> (element type, element values).
        cases = {
            "RgbVector": ("Rgb", [[1, 2, 3], [4, 5, 6]]),
            "RgbaVector": ("Rgba", [[1, 2, 3, 4]]),
            "Vec2fVector": ("Vec2f", [[1, 2]]),
            "Vec2dVector": ("Vec2d", [[1, 2]]),
            "Vec3fVector": ("Vec3f", [[1, 2, 3], [4, 5, 6]]),
            "Vec3dVector": ("Vec3d", [[1, 2, 3]]),
            "Vec4fVector": ("Vec4f", [[1, 2, 3, 4]]),
            "Vec4dVector": ("Vec4d", [[1, 2, 3, 4]]),
            "Mat4fVector": ("Mat4f", [IDENTITY4, RAMP4]),
            "Mat4dVector": ("Mat4d", [RAMP4]),
        }
        for name, (element, values) in cases.items():
            with self.subTest(name):
                elements = [getattr(scene_rdl2, element)(v) for v in values]
                self.assertValuesEqual(getattr(scene_rdl2, name)(elements), values)
                self.assertEqual(getattr(scene_rdl2, name)().toList(), [])


if __name__ == "__main__":
    unittest.main()
