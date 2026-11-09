# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestJoint. Joint has no Python class, so this
uses the generic SceneObject API on its node_xform attribute. See the bindings
README for the "Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, read_scene, write_scene


class TestJoint(Rdl2TestCase):

    XFORM = [[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 4, 0], [0, 0, 0, 1]]

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        joint = self.context.createSceneObject("Joint", "/joint")
        joint.set("node_xform", [v for row in self.XFORM for v in row])

    def check(self, context):
        joint = context.getSceneObject("/joint")
        self.assertIsNotNone(joint.toNode())
        self.assertEqual(joint.get("node_xform").toList(), self.XFORM)

    def round_trip(self, filename):
        path = self.temp_path(filename)
        write_scene(self.context, path)
        result = scene_rdl2.SceneContext()
        read_scene(result, path)
        self.check(result)

    def test_setup(self):
        # Mirrors TestJoint::testSetup.
        self.check(self.context)

    def test_ascii(self):
        # Mirrors TestJoint::testAscii.
        self.round_trip("Joint.rdla")

    def test_binary(self):
        # Mirrors TestJoint::testBinary.
        self.round_trip("Joint.rdlb")

    # TODO: bind Joint (new py_scene_rdl2_joint.cc) with SceneObject.toJoint(),
    # so getTypeName() stops reporting "UNKNOWN" for it.
    # def test_joint_type(self):
    #     joint = self.context.getSceneObject("/joint")
    #     self.assertIsInstance(joint.toJoint(), scene_rdl2.Joint)
    #     self.assertNotIn("UNKNOWN", joint.getTypeName())


if __name__ == "__main__":
    unittest.main()
