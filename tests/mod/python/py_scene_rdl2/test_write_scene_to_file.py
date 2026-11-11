# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""writeSceneToFile. There is no C++ test file for this function."""

import unittest

import scene_rdl2
from rdl2_test_util import (Rdl2TestCase, build_builtin_scene, build_roundtrip_scene,
                            check_builtin_scene, check_roundtrip_scene, make_context,
                            read_scene)


class TestWriteSceneToFile(Rdl2TestCase):

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        build_builtin_scene(self.context)

    def test_format_follows_extension(self):
        for ext in (".rdla", ".rdlb"):
            with self.subTest(ext):
                path = self.temp_path("scene" + ext)
                scene_rdl2.writeSceneToFile(self.context, path)
                result = scene_rdl2.SceneContext()
                read_scene(result, path)
                check_builtin_scene(self, result)

    def test_delta_and_skip_defaults_overload(self):
        path = self.temp_path("scene.rdla")
        scene_rdl2.writeSceneToFile(self.context, path, False, True)
        with open(path) as f:
            self.assertNotIn('["min_frame"]', f.read())

    def test_unknown_extension_raises(self):
        with self.assertRaises(RuntimeError):
            scene_rdl2.writeSceneToFile(self.context, self.temp_path("scene.txt"))

    def test_every_attribute_type(self):
        original = build_roundtrip_scene()
        for ext in (".rdla", ".rdlb"):
            with self.subTest(ext):
                path = self.temp_path("scene" + ext)
                scene_rdl2.writeSceneToFile(original, path)
                result = make_context()
                read_scene(result, path)
                check_roundtrip_scene(self, original, result)


if __name__ == "__main__":
    unittest.main()
