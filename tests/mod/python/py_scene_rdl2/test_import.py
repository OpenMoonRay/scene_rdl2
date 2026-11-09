# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Importing the module. There is no C++ test file for this."""

import unittest

import scene_rdl2


class TestImport(unittest.TestCase):

    def test_package_reexports_extension_module(self):
        from scene_rdl2 import __scene_rdl2__
        self.assertIs(scene_rdl2.SceneContext, __scene_rdl2__.SceneContext)


if __name__ == "__main__":
    unittest.main()
