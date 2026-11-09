# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestLayer. See the bindings README for the
"Mirrors" and "Omits" comments.

Python cannot make Layer assignments yet, so the live tests build them from
RDLA and inspect them through the generic attribute arrays ("geometries",
"parts", "surface_shaders", ...). The commented-out tests mirror the C++ tests
against a proposed Python API for the missing methods. Their assertions have
not run, since those methods do not exist yet."""

import unittest

import scene_rdl2
from rdl2_test_util import (Rdl2TestCase, make_context, names, read_scene,
                            requires_test_dsos, write_scene)


def layer_rows(layer):
    """Returns the layer's assignments as (geometry, part, material,
    light set, displacement, volume shader) name tuples, in assignment-id
    order."""
    return list(zip(names(layer.get("geometries").toList()),
                    layer.get("parts").toList(),
                    names(layer.get("surface_shaders").toList()),
                    names(layer.get("lightsets").toList()),
                    names(layer.get("displacements").toList()),
                    names(layer.get("volume_shaders").toList())))


# The objects TestLayer creates, as RDLA. Each test appends its own Layer.
LAYER_OBJECTS = """
teapot1 = FakeTeapot("/seq/shot/teapot1") {}
teapot2 = FakeTeapot("/seq/shot/teapot2") {}
teapot3 = FakeTeapot("/seq/shot/teapot3") {}
material1 = FakeMaterial("/seq/shot/material1") {}
material2 = FakeMaterial("/seq/shot/material2") {}
displacement1 = FakeDisplacement("/seq/shot/displacement1") {}
displacement2 = FakeDisplacement("/seq/shot/displacement2") {}
volumeShader1 = FakeVolumeShader("/seq/shot/volumeShader1") {}
volumeShader2 = FakeVolumeShader("/seq/shot/volumeShader2") {}
key = FakeLight("/seq/shot/key") {}
fill = FakeLight("/seq/shot/fill") {}
rim = FakeLight("/seq/shot/rim") {}
lights1 = LightSet("/seq/shot/keyfill") { key, fill }
lights2 = LightSet("/seq/shot/fillrim") { fill, rim }
"""


@requires_test_dsos
class TestLayer(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()

    def load(self, rdla):
        scene_rdl2.AsciiReader(self.context).fromString(LAYER_OBJECTS + rdla)

    def obj(self, name):
        return self.context.getSceneObject("/seq/shot/" + name)

    def test_clear_layer(self):
        # Mirrors TestLayer::testClearLayer.
        # Omits: assignment ids restarting at 0 (see the Layer TODO below).
        self.load("""
            Layer("/seq/shot/layer") {
                {teapot1, "lid", material1, lights1},
                {teapot1, "body", material1, lights1},
            }""")
        layer = self.obj("layer").toLayer()
        with self.assertRaises(RuntimeError):
            layer.clear()
        layer.beginUpdate()
        layer.clear()
        layer.endUpdate()
        self.assertEqual(layer.getAssignmentCount(), 0)
        self.assertFalse(layer.contains(self.obj("teapot1").toGeometry()))

    def test_context_lookup(self):
        # Mirrors TestLayer::testContextLookup.
        self.load("""
            Layer("/seq/shot/layer0") {
                {teapot1, "lid", material1, lights1, displacement1, volumeShader1},
                {teapot1, "body", material1, lights1},
            }
            Layer("/seq/shot/layer1") {
                {teapot1, "lid", material1, lights1, displacement1, volumeShader1},
                {teapot1, "body", material1, lights1},
                {teapot2, "lid", material2, lights2, displacement2, volumeShader2},
                {teapot2, "body", material2, lights2},
            }""")
        geomset0 = self.context.createSceneObject("GeometrySet", "/seq/shot/asset0").toGeometrySet()
        geomset1 = self.context.createSceneObject("GeometrySet", "/seq/shot/asset1").toGeometrySet()
        self.assertEqual(geomset0.get("geometries").toList(), [])
        self.assertEqual(geomset1.get("geometries").toList(), [])
        geomset0.beginUpdate()
        geomset0.add(self.obj("teapot1").toGeometry())   # Used in layer0 and layer1
        geomset0.add(self.obj("teapot2").toGeometry())   # Used in layer1
        geomset0.endUpdate()
        geomset1.beginUpdate()
        geomset1.add(self.obj("teapot2").toGeometry())   # Used in layer1
        geomset1.add(self.obj("teapot3").toGeometry())   # Not used in a layer
        geomset1.endUpdate()
        self.assertEqual(len(geomset0.get("geometries").toList()), 2)
        self.assertEqual(len(geomset1.get("geometries").toList()), 2)

        def geometry_sets_for(layer_name):
            indices = self.context.getGeometrySetIndicesForLayer(self.obj(layer_name).toLayer())
            return sorted(self.context.getGeometrySetAt(i).getName() for i in indices)

        self.assertEqual(geometry_sets_for("layer0"), ["/seq/shot/asset0"])
        self.assertEqual(geometry_sets_for("layer1"), ["/seq/shot/asset0", "/seq/shot/asset1"])

    def test_serialize(self):
        # Mirrors TestLayer::testSerialize.
        # Omits: Layer.assign (reading RDLA into the context makes the
        # assignments instead) and getAllGeometryToRootShaders (the attribute
        # arrays are checked instead). See the Layer TODO below.
        self.load("""
            Layer("/seq/shot/layer") {
                {teapot1, "lid", material1, lights1, displacement1, volumeShader1},
            }""")
        path = self.temp_path("layer.rdlb")
        write_scene(self.context, path)
        copy = make_context()
        read_scene(copy, path)
        copy.commitAllChanges()

        self.context.commitAllChanges()
        scene_rdl2.AsciiReader(self.context).fromString("""
            Layer("/seq/shot/layer") {
                {FakeTeapot("/seq/shot/teapot1"), "lid", FakeMaterial("/seq/shot/material2"),
                 LightSet("/seq/shot/keyfill"), FakeDisplacement("/seq/shot/displacement1"),
                 FakeVolumeShader("/seq/shot/volumeShader1")},
            }""")
        path = self.temp_path("layer_delta.rdlb")
        write_scene(self.context, path, delta_encoding=True)
        read_scene(copy, path)

        layer = copy.getSceneObject("/seq/shot/layer").toLayer()
        self.assertEqual(layer.getAssignmentCount(), 1)
        self.assertEqual(layer_rows(layer), [
            ("/seq/shot/teapot1", "", "/seq/shot/material2", "/seq/shot/keyfill",
             "/seq/shot/displacement1", "/seq/shot/volumeShader1")])

    # TODO: bind Layer.assign and the Layer lookups (py_scene_rdl2_layer.cc).
    # Python cannot build or query layer assignments directly. The tests below
    # mirror TestLayer::testAssignAndLookup, testDefaultAssignments,
    # testClearLayer, and testIterators against this proposed API:
    #   assign(geometry, partName, material, lightSet,
    #          displacement=None, volumeShader=None) -> assignment id
    #   lookup(assignmentId) / lookup(geometry, partName) -> (material, lightSet),
    #       raising IndexError for unknown assignments
    #   lookupDisplacement(id), lookupVolumeShader(id), lookupGeomAndPart(id)
    #   getAssignmentIds(sceneObject) -> ids of the assignments using a geometry,
    #       root shader, light set, displacement, or volume shader (begin()/end())
    #
    # def make_lights(self):
    #     # Helper for the tests below.
    #     self.load("")
    #     return self.obj("keyfill").toLightSet(), self.obj("fillrim").toLightSet()
    #
    # def assert_lookup(self, result, material, light_set):
    #     self.assertEqual(result[0].getName(), material.getName())
    #     self.assertEqual(result[1].getName(), light_set.getName())
    #
    # def test_assign_and_lookup(self):
    #     # Mirrors TestLayer::testAssignAndLookup.
    #     lights1, lights2 = self.make_lights()
    #     teapot1, teapot2 = (self.obj(n).toGeometry() for n in ("teapot1", "teapot2"))
    #     material1, material2 = (self.obj(n).toMaterial() for n in ("material1", "material2"))
    #     displacement1 = self.obj("displacement1").toDisplacement()
    #     displacement2 = self.obj("displacement2").toDisplacement()
    #     layer = self.context.createSceneObject("Layer", "/seq/shot/layer").toLayer()
    #
    #     layer.beginUpdate()
    #     self.assertEqual(layer.assign(teapot1, "lid", material1, lights1, displacement1), 0)
    #     self.assertEqual(layer.assign(teapot1, "body", material1, lights1), 1)
    #     layer.endUpdate()
    #     self.assert_lookup(layer.lookup(0), material1, lights1)
    #     self.assert_lookup(layer.lookup(teapot1, "lid"), material1, lights1)
    #     self.assert_lookup(layer.lookup(1), material1, lights1)
    #     self.assert_lookup(layer.lookup(teapot1, "body"), material1, lights1)
    #     with self.assertRaises(IndexError):
    #         layer.lookup(2)
    #     with self.assertRaises(IndexError):
    #         layer.lookup(teapot2, "lid")
    #     with self.assertRaises(IndexError):
    #         layer.lookup(teapot1, "spout")
    #
    #     # Reassignments reuse the same assignment id.
    #     layer.beginUpdate()
    #     self.assertEqual(layer.assign(teapot1, "lid", material2, lights2, displacement2), 0)
    #     layer.endUpdate()
    #     self.assert_lookup(layer.lookup(0), material2, lights2)
    #     self.assert_lookup(layer.lookup(teapot1, "lid"), material2, lights2)
    #
    #     # Same part names on different geometries are fine.
    #     layer.beginUpdate()
    #     layer.assign(teapot1, "lid", material1, lights1, displacement1)
    #     layer.assign(teapot1, "body", material1, lights1)
    #     layer.assign(teapot2, "lid", material2, lights2, displacement2)
    #     layer.assign(teapot2, "body", material2, lights2)
    #     layer.endUpdate()
    #     self.assert_lookup(layer.lookup(teapot1, "lid"), material1, lights1)
    #     self.assert_lookup(layer.lookup(teapot1, "body"), material1, lights1)
    #     self.assert_lookup(layer.lookup(teapot2, "lid"), material2, lights2)
    #     self.assert_lookup(layer.lookup(teapot2, "body"), material2, lights2)
    #
    # def test_default_assignments(self):
    #     # Mirrors TestLayer::testDefaultAssignments.
    #     lights1, _ = self.make_lights()
    #     teapot = self.obj("teapot1").toGeometry()
    #     material1, material2 = (self.obj(n).toMaterial() for n in ("material1", "material2"))
    #     displacement = self.obj("displacement1").toDisplacement()
    #     layer = self.context.createSceneObject("Layer", "/seq/shot/layer").toLayer()
    #     layer.beginUpdate()
    #     layer.assign(teapot, "lid", material1, lights1, displacement)
    #     layer.assign(teapot, "body", material1, lights1)
    #     layer.assign(teapot, "spout", material1, lights1, displacement)
    #     layer.endUpdate()
    #     self.assert_lookup(layer.lookup(teapot, "body"), material1, lights1)
    #     with self.assertRaises(IndexError):
    #         layer.lookup(teapot, "handle")
    #
    #     # A default ("") part assignment catches unassigned parts.
    #     layer.beginUpdate()
    #     layer.assign(teapot, "", material2, lights1, displacement)
    #     layer.endUpdate()
    #     self.assert_lookup(layer.lookup(teapot, "body"), material1, lights1)
    #     self.assert_lookup(layer.lookup(teapot, "handle"), material2, lights1)
    #
    # def test_clear_resets_assignment_ids(self):
    #     # Mirrors TestLayer::testClearLayer (the remainder).
    #     lights1, _ = self.make_lights()
    #     teapot = self.obj("teapot1").toGeometry()
    #     material = self.obj("material1").toMaterial()
    #     displacement = self.obj("displacement1").toDisplacement()
    #     layer = self.context.createSceneObject("Layer", "/seq/shot/layer").toLayer()
    #     layer.beginUpdate()
    #     self.assertEqual(layer.assign(teapot, "lid", material, lights1, displacement), 0)
    #     self.assertEqual(layer.assign(teapot, "body", material, lights1), 1)
    #     self.assertEqual(layer.assign(teapot, "spout", material, lights1, displacement), 2)
    #     layer.endUpdate()
    #     layer.beginUpdate()
    #     layer.clear()
    #     self.assertEqual(layer.assign(teapot, "handle", material, lights1, displacement), 0)
    #     layer.endUpdate()
    #
    # def test_iterators(self):
    #     # Mirrors TestLayer::testIterators.
    #     # Omits: its standalone FilterIndexIterator check, which is C++-only.
    #     lights1, lights2 = self.make_lights()
    #     teapot1, teapot2 = (self.obj(n).toGeometry() for n in ("teapot1", "teapot2"))
    #     material1, material2 = (self.obj(n).toMaterial() for n in ("material1", "material2"))
    #     displacement1 = self.obj("displacement1").toDisplacement()
    #     displacement2 = self.obj("displacement2").toDisplacement()
    #     volume1, volume2 = (self.obj(n) for n in ("volumeShader1", "volumeShader2"))
    #     layer = self.context.createSceneObject("Layer", "/seq/shot/layer").toLayer()
    #     layer.beginUpdate()
    #     layer.assign(teapot1, "lid", material1, lights1, displacement1, volume1)
    #     layer.assign(teapot1, "body", material1, lights1)
    #     layer.assign(teapot2, "lid", material2, lights2, displacement2, volume2)
    #     layer.assign(teapot2, "body", material2, lights2)
    #     layer.endUpdate()
    #
    #     for geometry in (teapot1, teapot2):
    #         ids = layer.getAssignmentIds(geometry)
    #         self.assertEqual(len(ids), 2)
    #         for i in ids:
    #             self.assertEqual(layer.lookupGeomAndPart(i)[0].getName(), geometry.getName())
    #     for material in (material1, material2):
    #         ids = layer.getAssignmentIds(material)
    #         self.assertEqual(len(ids), 2)
    #         for i in ids:
    #             self.assertEqual(layer.lookup(i)[0].getName(), material.getName())
    #     for light_set in (lights1, lights2):
    #         ids = layer.getAssignmentIds(light_set)
    #         self.assertEqual(len(ids), 2)
    #         for i in ids:
    #             self.assertEqual(layer.lookup(i)[1].getName(), light_set.getName())
    #     for displacement in (displacement1, displacement2):
    #         ids = layer.getAssignmentIds(displacement)
    #         self.assertEqual(len(ids), 1)
    #         self.assertEqual(layer.lookupDisplacement(ids[0]).getName(), displacement.getName())
    #     for volume in (volume1, volume2):
    #         ids = layer.getAssignmentIds(volume)
    #         self.assertEqual(len(ids), 1)
    #         self.assertEqual(layer.lookupVolumeShader(ids[0]).getName(), volume.getName())

    def test_rdla_assignments(self):
        self.load("""
            Layer("/seq/shot/layer") {
                {teapot1, "lid", material1, lights1, displacement1},
                {teapot1, "body", material1, lights1},
                {teapot2, "lid", material2, lights2, displacement2},
            }""")
        layer = self.obj("layer").toLayer()
        teapot1 = self.obj("teapot1").toGeometry()
        teapot2 = self.obj("teapot2").toGeometry()
        teapot3 = self.obj("teapot3").toGeometry()

        self.assertEqual(layer.getAssignmentCount(), 3)
        self.assertEqual(layer.getAssignmentId(teapot1, "lid"), 0)
        self.assertEqual(layer.getAssignmentId(teapot1, "body"), 1)
        self.assertEqual(layer.getAssignmentId(teapot2, "lid"), 2)
        self.assertEqual(layer.getAssignmentId(teapot1, "spout"), -1)
        self.assertTrue(layer.contains(teapot1))
        self.assertFalse(layer.contains(teapot3))
        self.assertEqual(layer_rows(layer), [
            ("/seq/shot/teapot1", "lid", "/seq/shot/material1", "/seq/shot/keyfill",
             "/seq/shot/displacement1", None),
            ("/seq/shot/teapot1", "body", "/seq/shot/material1", "/seq/shot/keyfill",
             None, None),
            ("/seq/shot/teapot2", "lid", "/seq/shot/material2", "/seq/shot/fillrim",
             "/seq/shot/displacement2", None),
        ])

    def test_volume_shader_assignments_cover_whole_geometry(self):
        # Layer::assign drops the part name of any assignment with a volume
        # shader, so it applies to the whole geometry.
        self.load("""
            Layer("/seq/shot/layer") {
                {teapot1, "lid", material1, lights1, displacement1, volumeShader1},
            }""")
        layer = self.obj("layer").toLayer()
        self.assertEqual(layer.get("parts").toList(), [""])
        self.assertEqual(layer.getAssignmentId(self.obj("teapot1").toGeometry(), ""), 0)


if __name__ == "__main__":
    unittest.main()
