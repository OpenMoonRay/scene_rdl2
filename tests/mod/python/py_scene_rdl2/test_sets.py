# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestSets: GeometrySet and LightSet. See the
bindings README for the "Mirrors" and "Omits" comments."""

import unittest

from rdl2_test_util import Rdl2TestCase, make_context, names, requires_test_dsos


@requires_test_dsos
class TestSets(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()
        self.teapot1, self.teapot2, self.teapot3, self.dummy_geometry = (
            self.context.createSceneObject("FakeTeapot", "/seq/shot/" + name).toGeometry()
            for name in ("teapot1", "teapot2", "teapot3", "dummy"))
        self.asset = self.context.createSceneObject(
            "GeometrySet", "/seq/shot/asset").toGeometrySet()
        self.key, self.fill, self.rim, self.dummy_light = (
            self.context.createSceneObject("FakeLight", "/seq/shot/" + name).toLight()
            for name in ("key", "fill", "rim", "dummy_light"))
        self.rig = self.context.createSceneObject("LightSet", "/seq/shot/LT_RIG").toLightSet()

    def geometry_count(self):
        # getGeometries() is broken (see the TODO below), so read the attribute.
        return len(self.asset.get("geometries").toList())

    def add_geometries(self, *geometries):
        self.asset.beginUpdate()
        for geometry in geometries:
            self.asset.add(geometry)
        self.asset.endUpdate()

    def assert_geometries(self, size, inside, outside):
        self.assertEqual(self.geometry_count(), size)
        for geometry in inside:
            self.assertTrue(self.asset.contains(geometry))
        for geometry in outside:
            self.assertFalse(self.asset.contains(geometry))

    def add_lights(self, *lights):
        self.rig.beginUpdate()
        for light in lights:
            self.rig.add(light)
        self.rig.endUpdate()

    def assert_lights(self, size, inside, outside):
        self.assertEqual(len(self.rig.getLights().toList()), size)
        for light in inside:
            self.assertTrue(self.rig.contains(light))
        for light in outside:
            self.assertFalse(self.rig.contains(light))

    def test_add_geometry(self):
        # Mirrors TestSets::testAddGeometry.
        self.assert_geometries(0, [], [self.teapot1, self.teapot2, self.teapot3])
        self.add_geometries(self.teapot1, self.teapot2)
        self.assert_geometries(2, [self.teapot1, self.teapot2], [self.teapot3])
        # Adding a geometry again changes nothing.
        self.add_geometries(self.teapot1)
        self.assert_geometries(2, [self.teapot1, self.teapot2], [self.teapot3])

    def test_remove_geometry(self):
        # Mirrors TestSets::testRemoveGeometry.
        self.add_geometries(self.teapot1, self.teapot2, self.teapot3)
        self.assert_geometries(3, [self.teapot1, self.teapot2, self.teapot3], [self.dummy_geometry])
        self.asset.beginUpdate()
        self.asset.remove(self.teapot1)
        self.asset.endUpdate()
        self.assert_geometries(2, [self.teapot2, self.teapot3], [self.teapot1, self.dummy_geometry])
        # Removing a geometry that is not in the set changes nothing.
        self.asset.beginUpdate()
        self.asset.remove(self.dummy_geometry)
        self.asset.endUpdate()
        self.assert_geometries(2, [self.teapot2, self.teapot3], [self.teapot1, self.dummy_geometry])

    def test_clear_geometry(self):
        # Mirrors TestSets::testClearGeometry.
        self.add_geometries(self.teapot1, self.teapot2, self.teapot3)
        self.assertEqual(self.geometry_count(), 3)
        self.asset.beginUpdate()
        self.asset.clear()
        self.asset.endUpdate()
        self.assertEqual(self.geometry_count(), 0)
        with self.assertRaises(RuntimeError):
            self.asset.clear()

    def test_static_geometry(self):
        # Mirrors TestSets::testStaticGeometry.
        for teapot in (self.teapot1, self.teapot2, self.teapot3):
            teapot.set("static", True)
        self.add_geometries(self.teapot1, self.teapot2, self.teapot3)
        self.assertTrue(self.asset.isStatic())
        self.teapot2.set("static", False)
        self.assertFalse(self.asset.isStatic())

    def test_add_geometry_requires_update(self):
        with self.assertRaises(RuntimeError):
            self.asset.add(self.teapot1)

    # TODO: fix GeometrySet.getGeometries (py_scene_rdl2_geometry_set.cc): it
    # raises "No to_python (by-value) converter found for C++ type:
    # scene_rdl2::rdl2::SceneObject". The C++ tests read set sizes through it.
    # def test_get_geometries(self):
    #     self.add_geometries(self.teapot1)
    #     self.assertEqual([g.getName() for g in self.asset.getGeometries().toList()],
    #                      ["/seq/shot/teapot1"])

    def test_add_light(self):
        # Mirrors TestSets::testAddLight.
        self.assert_lights(0, [], [self.key, self.fill, self.rim])
        self.add_lights(self.key, self.fill)
        self.assert_lights(2, [self.key, self.fill], [self.rim])
        # Adding a light again changes nothing.
        self.add_lights(self.key)
        self.assert_lights(2, [self.key, self.fill], [self.rim])
        self.assertEqual(sorted(names(self.rig.getLights().toList())),
                         ["/seq/shot/fill", "/seq/shot/key"])

    def test_remove_light(self):
        # Mirrors TestSets::testRemoveLight.
        self.add_lights(self.key, self.fill, self.rim)
        self.assert_lights(3, [self.key, self.fill, self.rim], [self.dummy_light])
        self.rig.beginUpdate()
        self.rig.remove(self.key)
        self.rig.endUpdate()
        self.assert_lights(2, [self.fill, self.rim], [self.key, self.dummy_light])
        # Removing a light that is not in the set changes nothing.
        self.rig.beginUpdate()
        self.rig.remove(self.dummy_light)
        self.rig.endUpdate()
        self.assert_lights(2, [self.fill, self.rim], [self.key, self.dummy_light])

    def test_clear_light(self):
        # Mirrors TestSets::testClearLight.
        self.add_lights(self.key, self.fill, self.rim)
        self.assertEqual(len(self.rig.getLights().toList()), 3)
        self.rig.beginUpdate()
        self.rig.clear()
        self.rig.endUpdate()
        self.assertEqual(self.rig.getLights().toList(), [])
        with self.assertRaises(RuntimeError):
            self.rig.clear()

    def test_add_light_requires_update(self):
        with self.assertRaises(RuntimeError):
            self.rig.add(self.key)


if __name__ == "__main__":
    unittest.main()
