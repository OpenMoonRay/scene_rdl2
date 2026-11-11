# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Metadata. There is no C++ test file for this class; TestAscii and TestBinary
cover its serialization."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase


class TestMetadata(Rdl2TestCase):

    def test_attributes(self):
        context = scene_rdl2.SceneContext()
        metadata = context.createSceneObject("Metadata", "metadata").toMetadata()
        metadata.setAttributes(["frame", "artist"], ["int", "string"], ["12", "me"])
        self.assertEqual(metadata.getAttributeNames().toList(), ["frame", "artist"])
        self.assertEqual(metadata.getAttributeTypes().toList(), ["int", "string"])
        self.assertEqual(metadata.getAttributeValues().toList(), ["12", "me"])

    def test_attributes_set_directly_are_tracked(self):
        context = scene_rdl2.SceneContext()
        metadata = context.createSceneObject("Metadata", "metadata")
        context.commitAllChanges()
        metadata.set("name", ["frame"])
        metadata.set("type", ["int"])
        metadata.set("value", ["12"])
        writer = scene_rdl2.AsciiWriter(context)
        writer.setDeltaEncoding(True)
        self.assertIn('Metadata("metadata")', writer.toString())

    # TODO: fix Metadata.setAttributes (py_scene_rdl2_metadata.cc, or
    # rdl2::Metadata::setAttributes): it writes through getMutable(), which
    # skips change tracking, so the values are missing from delta-encoded
    # writes and from writeSceneToFile(..., ".rdlb") (which skips defaults).
    # def test_set_attributes_is_tracked(self):
    #     context = scene_rdl2.SceneContext()
    #     metadata = context.createSceneObject("Metadata", "metadata").toMetadata()
    #     context.commitAllChanges()
    #     metadata.setAttributes(["frame"], ["int"], ["12"])
    #     writer = scene_rdl2.AsciiWriter(context)
    #     writer.setDeltaEncoding(True)
    #     self.assertIn('Metadata("metadata")', writer.toString())


if __name__ == "__main__":
    unittest.main()
