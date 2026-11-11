# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestRenderOutput. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, read_scene, write_scene


class TestRenderOutput(Rdl2TestCase):

    def setUp(self):
        self.context = scene_rdl2.SceneContext()
        self.output = self.context.createSceneObject(
            "RenderOutput", "/renderOutput").toRenderOutput()

    def configure(self):
        """The values TestRenderOutput::setUp sets."""
        RO = scene_rdl2.RenderOutput
        output = self.output
        output.beginUpdate()
        output.setActive(False)
        output.setResult(RO.Result.DEPTH)
        output.setStateVariable(RO.StateVariable.P)
        output.setPrimitiveAttribute("surface_st")
        output.setPrimitiveAttributeType(RO.PrimitiveAttributeType.VEC2F)
        output.setMaterialAov("diffuse")
        output.setLpe("CD*L")
        output.setFileName("foo.exr")
        output.setFilePart("bar_part")
        output.setCompression(RO.Compression.DWAA)
        output.setChannelName("baz_channel")
        output.setChannelFormat(RO.ChannelFormat.FLOAT)
        output.endUpdate()
        # No accessors are bound for these yet; see the TODO below.
        output.set("checkpoint_file_name", "qux.exr")
        output.set("resume_file_name", "quux.exr")

    def check(self, context):
        RO = scene_rdl2.RenderOutput
        output = context.getSceneObject("/renderOutput").toRenderOutput()
        self.assertFalse(output.getActive())
        self.assertEqual(output.getResult(), RO.Result.DEPTH)
        self.assertEqual(output.getStateVariable(), RO.StateVariable.P)
        self.assertEqual(output.getPrimitiveAttribute(), "surface_st")
        self.assertEqual(output.getPrimitiveAttributeType(), RO.PrimitiveAttributeType.VEC2F)
        self.assertEqual(output.getMaterialAov(), "diffuse")
        self.assertEqual(output.getLpe(), "CD*L")
        self.assertEqual(output.getFileName(), "foo.exr")
        self.assertEqual(output.getFilePart(), "bar_part")
        self.assertEqual(output.getCompression(), RO.Compression.DWAA)
        self.assertEqual(output.getChannelName(), "baz_channel")
        self.assertEqual(output.getChannelFormat(), RO.ChannelFormat.FLOAT)
        self.assertEqual(output.get("checkpoint_file_name"), "qux.exr")
        self.assertEqual(output.get("resume_file_name"), "quux.exr")

    def round_trip(self, filename):
        self.configure()
        path = self.temp_path(filename)
        write_scene(self.context, path)
        result = scene_rdl2.SceneContext()
        read_scene(result, path)
        self.check(result)

    def test_setup(self):
        # Mirrors TestRenderOutput::testSetup. Its checks of the default values
        # are in test_defaults.
        # Omits: SceneContext.getAllRenderOutputs and the checkpoint and resume
        # file-name accessors (see the TODO below).
        self.configure()
        self.check(self.context)

    def test_ascii(self):
        # Mirrors TestRenderOutput::testAscii.
        self.round_trip("RenderOutput.rdla")

    def test_binary(self):
        # Mirrors TestRenderOutput::testBinary.
        self.round_trip("RenderOutput.rdlb")

    # TODO: bind RenderOutput.get/setCheckpointFileName and
    # get/setResumeFileName (py_scene_rdl2_render_output.cc), and
    # SceneContext.getAllRenderOutputs (py_scene_rdl2_scene_context.cc), all
    # used by TestRenderOutput.
    # def test_checkpoint_accessors_and_render_output_list(self):
    #     # Mirrors TestRenderOutput::testSetup (the remainder).
    #     self.configure()
    #     outputs = self.context.getAllRenderOutputs()
    #     self.assertEqual([o.getName() for o in outputs], ["/renderOutput"])
    #     output = outputs[0]
    #     self.assertEqual(output.getCheckpointFileName(), "qux.exr")
    #     self.assertEqual(output.getResumeFileName(), "quux.exr")
    #     output.beginUpdate()
    #     output.setCheckpointFileName("other.exr")
    #     output.setResumeFileName("")
    #     output.endUpdate()
    #     self.assertEqual(output.getCheckpointFileName(), "other.exr")

    def test_defaults(self):
        RO = scene_rdl2.RenderOutput
        self.assertTrue(self.output.getActive())
        self.assertEqual(self.output.getResult(), RO.Result.BEAUTY)
        self.assertEqual(self.output.getOutputType(), "flat")
        self.assertEqual(self.output.getFileName(), "scene.exr")
        self.assertEqual(self.output.getCompression(), RO.Compression.ZIP)
        self.assertEqual(self.output.getChannelFormat(), RO.ChannelFormat.HALF)
        self.assertEqual(self.output.getMathFilter(), RO.MathFilter.AVG)
        self.assertEqual(self.output.getStateVariable(), RO.StateVariable.N)
        self.assertEqual(self.output.getPrimitiveAttributeType(),
                         RO.PrimitiveAttributeType.FLOAT)
        self.assertEqual(self.output.getChannelName(), "")
        self.assertEqual(self.output.getLpe(), "")
        self.assertEqual(self.output.getMaterialAov(), "")
        self.assertEqual(self.output.getPrimitiveAttribute(), "")
        self.assertEqual(self.output.getFilePart(), "")
        self.assertEqual(self.output.get("checkpoint_file_name"), "checkpoint.exr")
        self.assertEqual(self.output.get("resume_file_name"), "")
        self.assertIsNone(self.output.getExrHeaderAttributes())

    def test_setters_require_update(self):
        with self.assertRaises(RuntimeError):
            self.output.setFileName("other.exr")

    def test_setters_not_in_setup(self):
        # The setters TestRenderOutput::setUp does not call.
        self.output.beginUpdate()
        self.output.setCompressionLevel(3.5)
        self.output.setMathFilter(scene_rdl2.RenderOutput.MathFilter.MAX)
        self.output.endUpdate()
        self.assertEqual(self.output.getCompressionLevel(), 3.5)
        self.assertEqual(self.output.getMathFilter(), scene_rdl2.RenderOutput.MathFilter.MAX)


if __name__ == "__main__":
    unittest.main()
