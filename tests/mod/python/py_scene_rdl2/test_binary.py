# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestBinary. See the bindings README for the
"Mirrors" and "Omits" comments."""

import os
import unittest

import scene_rdl2
from rdl2_test_util import (Rdl2TestCase, build_builtin_scene, check_builtin_scene,
                            check_delta_encoding, check_null_references, check_roundtrip)


class TestBinary(Rdl2TestCase):

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        build_builtin_scene(self.context)

    def test_roundtrip(self):
        # Mirrors TestBinary::testRoundtrip.
        check_roundtrip(self, "roundtrip.rdlb")

    def test_transient_encoding(self):
        # Mirrors TestBinary::testTransientEncoding.
        check_roundtrip(self, "transient.rdlb", transient_encoding=True)

    def test_delta_encoding(self):
        # Mirrors TestBinary::testDeltaEncoding.
        check_delta_encoding(self, ".rdlb")

    def test_null_references(self):
        # Mirrors TestBinary::testNullReferences.
        check_null_references(self, ".rdlb")

    def test_file_round_trip(self):
        path = self.temp_path("scene.rdlb")
        scene_rdl2.BinaryWriter(self.context).toFile(path)
        result = scene_rdl2.SceneContext()
        scene_rdl2.BinaryReader(result).fromFile(path)
        check_builtin_scene(self, result)

    def test_skip_defaults(self):
        writer = scene_rdl2.BinaryWriter(self.context)
        full_path = self.temp_path("full.rdlb")
        writer.toFile(full_path)
        writer.setSkipDefaults(True)
        skipped_path = self.temp_path("skipped.rdlb")
        writer.toFile(skipped_path)
        self.assertLess(os.path.getsize(skipped_path), os.path.getsize(full_path))
        result = scene_rdl2.SceneContext()
        scene_rdl2.BinaryReader(result).fromFile(skipped_path)
        check_builtin_scene(self, result)

    # TODO: bind BinaryWriter.toBytes and BinaryReader.fromBytes
    # (py_scene_rdl2_misc.cc). The C++ tests stream binary scenes through
    # memory (toStream/fromStream); Python can only go through files.
    # def test_bytes_round_trip(self):
    #     data = scene_rdl2.BinaryWriter(self.context).toBytes()
    #     result = scene_rdl2.SceneContext()
    #     scene_rdl2.BinaryReader(result).fromBytes(data)
    #     check_builtin_scene(self, result)


if __name__ == "__main__":
    unittest.main()
