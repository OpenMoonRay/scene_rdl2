# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestAscii. See the bindings README for the
"Mirrors" and "Omits" comments."""

import struct
import unittest

import scene_rdl2
from rdl2_test_util import (Rdl2TestCase, build_builtin_scene, check_builtin_scene,
                            check_delta_encoding, check_null_references, check_roundtrip,
                            make_context)


class TestAscii(Rdl2TestCase):

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        build_builtin_scene(self.context)

    def test_roundtrip(self):
        # Mirrors TestAscii::testRoundtrip.
        check_roundtrip(self, "roundtrip.rdla")

    def test_delta_encoding(self):
        # Mirrors TestAscii::testDeltaEncoding.
        check_delta_encoding(self, ".rdla")

    def test_null_references(self):
        # Mirrors TestAscii::testNullReferences.
        check_null_references(self, ".rdla")

    def test_attribute_alias(self):
        # Mirrors TestAscii::testAttributeAlias.
        context = make_context()
        scene_rdl2.AsciiReader(context).fromString(
            'ExtensiveObject("/seq/shot/pizza") {\n'
            '    ["bool vector"] = { false, true, false},\n'
            '    ["int vector"] = { 1, 2, 3},\n'
            '}\n')
        pizza = context.getSceneObject("/seq/shot/pizza")
        self.assertEqual(pizza.get("bool_vector").toList(), [False, True, False])
        self.assertEqual(pizza.get("int_vector").toList(), [1, 2, 3])
        # get() also resolves aliases.
        self.assertEqual(pizza.get("int vector").toList(), [1, 2, 3])

    def test_denormals(self):
        # Mirrors TestAscii::testDenormals, which TestAscii.h currently leaves
        # out of the C++ suite for being slow.
        # Omits: most denormal values. The C++ test walks all 2^23 of each sign;
        # this checks the smallest and largest 256 of each sign, to stay quick.
        smallest = 2.0 ** -149
        for sign in (1, -1):
            for first_bits in (1, 0x7fffff - 255):
                with self.subTest(sign=sign, first_bits=first_bits):
                    values = [sign * (first_bits + i) * smallest for i in range(256)]
                    context = make_context()
                    scene_rdl2.AsciiReader(context).fromString(
                        'ExtensiveObject("/seq/shot/pizza") {\n'
                        '    ["float_vector"] = { %s },\n'
                        '}\n' % ", ".join("%.8g" % v for v in values))
                    floats = context.getSceneObject("/seq/shot/pizza").get(
                        "float_vector").toList()
                    sign_bit = 0x80000000 if sign < 0 else 0
                    expected = [sign_bit | (first_bits + i) for i in range(256)]
                    self.assertEqual([struct.unpack("<I", struct.pack("<f", f))[0]
                                      for f in floats], expected)

    def test_string_round_trip(self):
        text = scene_rdl2.AsciiWriter(self.context).toString()
        self.assertIn('UserData("data")', text)
        self.assertIn('["image_width"] = 640', text)

        result = scene_rdl2.SceneContext()
        scene_rdl2.AsciiReader(result).fromString(text)
        check_builtin_scene(self, result)

    def test_file_round_trip(self):
        path = self.temp_path("scene.rdla")
        scene_rdl2.AsciiWriter(self.context).toFile(path)
        result = scene_rdl2.SceneContext()
        scene_rdl2.AsciiReader(result).fromFile(path)
        check_builtin_scene(self, result)

    def test_skip_defaults(self):
        writer = scene_rdl2.AsciiWriter(self.context)
        self.assertIn('["min_frame"]', writer.toString())
        writer.setSkipDefaults(True)
        text = writer.toString()
        self.assertNotIn('["min_frame"]', text)
        self.assertIn('["image_width"] = 640', text)

    def test_delta_encoding_to_string(self):
        self.context.commitAllChanges()
        self.context.getSceneVariables().set("image_width", 800)
        writer = scene_rdl2.AsciiWriter(self.context)
        writer.setDeltaEncoding(True)
        text = writer.toString()
        self.assertIn('["image_width"] = 800', text)
        self.assertNotIn('UserData("data")', text)

    def test_read_errors(self):
        reader = scene_rdl2.AsciiReader(scene_rdl2.SceneContext())
        with self.assertRaises(RuntimeError):
            reader.fromString("this is not lua {")
        with self.assertRaises(RuntimeError):
            reader.fromFile(self.temp_path("missing.rdla"))


if __name__ == "__main__":
    unittest.main()
