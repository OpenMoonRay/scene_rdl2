# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestTraceSet. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, make_context, names, read_scene, write_scene


TRACE_SET_RDLA = """
teapot1 = FakeTeapot("/seq/shot/teapot1") {}
teapot2 = FakeTeapot("/seq/shot/teapot2") {}
TraceSet("/seq/shot/traceset") {
    {teapot1, "lid"}, {teapot1, "spout"}, {teapot2, "lid"}, {teapot2, "body"},
}
"""


class TestTraceSet(Rdl2TestCase):

    def test_serialize(self):
        # Mirrors TestTraceSet::testSerialize.
        # Omits: TraceSet's assign, getAssignmentCount, getAssignmentId, contains,
        # and lookupGeomAndPart. TraceSet has no Python class, so this builds it
        # from RDLA and reads the generic attributes (see the TODO below).
        context = make_context()
        scene_rdl2.AsciiReader(context).fromString(TRACE_SET_RDLA)
        path = self.temp_path("traceset.rdlb")
        write_scene(context, path)
        copy = make_context()
        read_scene(copy, path)
        copy.commitAllChanges()

        context.commitAllChanges()
        scene_rdl2.AsciiReader(context).fromString(TRACE_SET_RDLA.replace(
            '{teapot2, "body"},', '{teapot2, "body"}, {teapot2, "base"},'))
        path = self.temp_path("traceset_delta.rdlb")
        write_scene(context, path, delta_encoding=True)
        # A delta holding the TraceSet also recreates the geometries it uses, so
        # as in the C++ test, it reads into an empty context.
        result = make_context()
        read_scene(result, path)

        trace_set = result.getSceneObject("/seq/shot/traceset")
        self.assertEqual(names(trace_set.get("geometries").toList()),
                         ["/seq/shot/teapot1"] * 2 + ["/seq/shot/teapot2"] * 3)
        self.assertEqual(trace_set.get("parts").toList(),
                         ["lid", "spout", "lid", "body", "base"])

    # TODO: bind TraceSet (new py_scene_rdl2_trace_set.cc): a TraceSet class
    # with toTraceSet(), assign(), getAssignmentCount(), getAssignmentId(),
    # contains(), and lookupGeomAndPart().
    # def test_trace_set_api(self):
    #     # Mirrors TestTraceSet::testSerialize (the remainder).
    #     context = make_context()
    #     teapot1 = context.createSceneObject("FakeTeapot", "/seq/shot/teapot1").toGeometry()
    #     teapot2 = context.createSceneObject("FakeTeapot", "/seq/shot/teapot2").toGeometry()
    #     trace_set = context.createSceneObject("TraceSet", "/seq/shot/traceset").toTraceSet()
    #     trace_set.beginUpdate()
    #     self.assertEqual(trace_set.assign(teapot1, "lid"), 0)
    #     self.assertEqual(trace_set.assign(teapot1, "spout"), 1)
    #     self.assertEqual(trace_set.assign(teapot2, "lid"), 2)
    #     self.assertEqual(trace_set.assign(teapot2, "body"), 3)
    #     self.assertEqual(trace_set.assign(teapot2, "base"), 4)
    #     trace_set.endUpdate()
    #     self.assertEqual(trace_set.getAssignmentCount(), 5)
    #     self.assertEqual(trace_set.getAssignmentId(teapot2, "base"), 4)
    #     self.assertTrue(trace_set.contains(teapot1))
    #     geometry, part = trace_set.lookupGeomAndPart(1)
    #     self.assertEqual((geometry.getName(), part), ("/seq/shot/teapot1", "spout"))


if __name__ == "__main__":
    unittest.main()
