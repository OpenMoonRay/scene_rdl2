# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestSceneContext. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, make_context, requires_test_dsos


BUILTIN_CLASSES = [
    "GeometrySet", "Joint", "Layer", "LightFilterSet", "LightSet", "Metadata",
    "RenderOutput", "SceneVariables", "ShadowReceiverSet", "ShadowSet",
    "TraceSet", "UserData",
]


class TestSceneContext(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()

    def test_dso_path(self):
        # Mirrors TestSceneContext::testDsoPath.
        self.context.setDsoPath("one:two:three")
        self.assertEqual(self.context.getDsoPath(), "one:two:three")

    @requires_test_dsos
    def test_create_scene_class(self):
        # Mirrors TestSceneContext::testCreateSceneClass.
        scene_class = self.context.createSceneClass("ExampleObject")
        self.assertEqual(scene_class.getName(), "ExampleObject")
        self.assertEqual(self.context.createSceneClass("ExampleObject").getName(),
                         "ExampleObject")
        self.assertEqual(self.context.getSceneClassNames().count("ExampleObject"), 1)

    @requires_test_dsos
    def test_get_scene_class(self):
        # Mirrors TestSceneContext::testGetSceneClass.
        self.context.createSceneClass("ExampleObject")
        self.assertEqual(self.context.getSceneClass("ExampleObject").getName(),
                         "ExampleObject")
        with self.assertRaises(ValueError):
            self.context.getSceneClass("NotASceneClass")

    @requires_test_dsos
    def test_scene_class_exists(self):
        # Mirrors TestSceneContext::testSceneClassExists.
        self.assertFalse(self.context.sceneClassExists("ExampleObject"))
        self.context.createSceneClass("ExampleObject")
        self.assertTrue(self.context.sceneClassExists("ExampleObject"))
        self.assertFalse(self.context.sceneClassExists("NotASceneClass"))

    @requires_test_dsos
    def test_iterate_scene_classes(self):
        # Mirrors TestSceneContext::testIterateSceneClasses.
        self.context.createSceneClass("ExampleObject")
        names = self.context.getSceneClassNames()
        for name in ("SceneVariables", "ExampleObject"):
            self.assertEqual(names.count(name), 1)
        for name in names:
            self.assertEqual(self.context.getSceneClass(name).getName(), name)

    @requires_test_dsos
    def test_create_scene_object(self):
        # Mirrors TestSceneContext::testCreateSceneObject. C++ compares pointers;
        # Python wrappers have no identity, so this checks a change made through
        # one object is visible through the other.
        pizza = self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        self.assertEqual(pizza.getName(), "/seq/shot/pizza")
        again = self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        pizza.set("awesomeness", 42)
        self.assertEqual(again.get("awesomeness"), 42)

    @requires_test_dsos
    def test_get_scene_object(self):
        # Mirrors TestSceneContext::testGetSceneObject, with the same substitute
        # for pointer comparison as test_create_scene_object.
        pizza = self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        found = self.context.getSceneObject("/seq/shot/pizza")
        self.assertEqual(found.getName(), "/seq/shot/pizza")
        pizza.set("awesomeness", 42)
        self.assertEqual(found.get("awesomeness"), 42)
        with self.assertRaises(ValueError):
            self.context.getSceneObject("/seq/shot/not_a_pizza")

    @requires_test_dsos
    def test_scene_object_exists(self):
        # Mirrors TestSceneContext::testSceneObjectExists.
        self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        self.assertTrue(self.context.sceneObjectExists("/seq/shot/pizza"))
        self.assertFalse(self.context.sceneObjectExists("/seq/shot/not_a_pizza"))

    @requires_test_dsos
    def test_iterate_scene_objects(self):
        # Mirrors TestSceneContext::testIterateSceneObjects.
        self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        self.context.createSceneObject("ExampleObject", "/seq/shot/cookie")
        names = self.context.getSceneObjectNames()
        self.assertEqual(sorted(names),
                         ["/seq/shot/cookie", "/seq/shot/pizza", "__SceneVariables__"])
        for name in names:
            self.assertEqual(self.context.getSceneObject(name).getName(), name)

    @requires_test_dsos
    def test_set_scene_object(self):
        # Mirrors TestSceneContext::testSetSceneObject.
        self.context.createSceneObject("ExampleObject", "/seq/shot/pizza")
        first = self.context.getSceneObject("/seq/shot/pizza")
        self.assertEqual(first.get("awesomeness"), 11)
        second = self.context.getSceneObject("/seq/shot/pizza")
        second.set("awesomeness", 42)
        self.assertEqual(second.get("awesomeness"), 42)
        self.assertEqual(first.get("awesomeness"), 42)

    @requires_test_dsos
    def test_load_all_scene_classes(self):
        # Mirrors TestSceneContext::testLoadAllSceneClasses. In proxy mode the
        # misbehaving test DSOs load without running their constructors.
        context = make_context(proxy_mode=True)
        context.loadAllSceneClasses()
        loaded = set(context.getSceneClassNames())
        for name in ["DeclareAndCreateObject", "DeclareAndDestroyObject",
                     "ExampleObject", "ExtensiveObject", "FakeLight",
                     "FakeMaterial", "FakeTeapot", "LibLadenCamera",
                     "LibLadenDisplayFilter", "LibLadenEnvMap",
                     "LibLadenGeometry", "LibLadenLight", "LibLadenLightFilter",
                     "LibLadenMap", "LibLadenNormalMap", "LibLadenMaterial",
                     "ThrowDuringConstruct", "UpdateTracker"]:
            self.assertIn(name, loaded)

    def test_scene_variables(self):
        # Mirrors TestSceneContext::testSceneVariables.
        scene_vars = self.context.getSceneVariables()
        self.assertFalse(scene_vars.get("checkpoint_active"))
        self.assertEqual(scene_vars.get("checkpoint_interval"), 15.0)
        self.assertEqual(scene_vars.get("checkpoint_time_cap"), 0.0)
        self.assertFalse(scene_vars.get("resumable_output"))
        self.assertFalse(scene_vars.get("resume_render"))

        scene_vars.set("checkpoint_active", True)
        scene_vars.set("checkpoint_interval", 5.0)
        scene_vars.set("checkpoint_time_cap", 1.0)
        scene_vars.set("resumable_output", True)
        scene_vars.set("resume_render", True)
        self.assertTrue(scene_vars.get("checkpoint_active"))
        self.assertEqual(scene_vars.get("checkpoint_interval"), 5.0)
        self.assertEqual(scene_vars.get("checkpoint_time_cap"), 1.0)
        self.assertTrue(scene_vars.get("resumable_output"))
        self.assertTrue(scene_vars.get("resume_render"))

        other = self.context.createSceneObject("SceneVariables", "MoreVariables")
        self.assertEqual(other.getName(), "__SceneVariables__")

    @requires_test_dsos
    def test_create_class_failure(self):
        # Mirrors TestSceneContext::testCreateClassFailure.
        count = len(self.context.getSceneClassNames())
        with self.assertRaises(RuntimeError):
            self.context.createSceneClass("ThrowDuringDeclare")
        self.assertEqual(len(self.context.getSceneClassNames()), count)

    @requires_test_dsos
    def test_create_object_failure(self):
        # Mirrors TestSceneContext::testCreateObjectFailure.
        count = len(self.context.getSceneObjectNames())
        with self.assertRaises(RuntimeError):
            self.context.createSceneObject("ThrowDuringConstruct", "/seq/shot/object")
        self.assertEqual(len(self.context.getSceneObjectNames()), count)

    def test_builtin_scene_classes(self):
        self.assertEqual(sorted(self.context.getSceneClassNames()), BUILTIN_CLASSES)
        self.assertTrue(self.context.sceneClassExists("UserData"))
        self.assertFalse(self.context.sceneClassExists("NoSuchClass"))

    def test_new_context_holds_only_scene_variables(self):
        self.assertEqual(self.context.getSceneObjectNames(), ["__SceneVariables__"])
        self.assertIsInstance(self.context.getSceneVariables(), scene_rdl2.SceneVariables)

    def test_proxy_mode(self):
        self.assertFalse(self.context.getProxyModeEnabled())
        self.context.setProxyModeEnabled(True)
        self.assertTrue(self.context.getProxyModeEnabled())

    def test_create_get_delete_object(self):
        obj = self.context.createSceneObject("UserData", "data")
        self.assertEqual(obj.getName(), "data")
        self.assertTrue(self.context.sceneObjectExists("data"))
        self.assertEqual(self.context.getSceneObject("data").getName(), "data")
        self.assertIn("data", self.context.getSceneObjectNames())
        self.assertEqual(self.context.getSceneObjectNamesAndTypes()["data"],
                         "GENERIC (SceneObject) | USERDATA")

        self.context.deleteSceneObject("data")
        self.assertFalse(self.context.sceneObjectExists("data"))
        with self.assertRaises(ValueError):
            self.context.deleteSceneObject("data")

    def test_create_existing_object_returns_it(self):
        self.context.createSceneObject("UserData", "data")
        again = self.context.createSceneObject("UserData", "data")
        self.assertEqual(again.getName(), "data")
        self.assertEqual(self.context.getSceneObjectNames().count("data"), 1)

    def test_create_existing_name_with_other_class_raises(self):
        self.context.createSceneObject("UserData", "data")
        with self.assertRaises(RuntimeError):
            self.context.createSceneObject("Metadata", "data")

    def test_scene_variables_cannot_be_deleted(self):
        with self.assertRaises(ValueError):
            self.context.deleteSceneObject("__SceneVariables__")

    def test_unknown_class_raises(self):
        self.context.setDsoPath("")
        with self.assertRaises(RuntimeError):
            self.context.createSceneClass("NoSuchClass")
        with self.assertRaises(RuntimeError):
            self.context.createSceneObject("NoSuchClass", "obj")

    def test_render_to_world(self):
        self.assertIsNone(self.context.getRender2World())
        # Held in a local until the test ends; see the TODO below.
        render2world = scene_rdl2.Mat4d(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [5, 6, 7, 1]])
        self.context.setRender2World(render2world)
        self.assertEqual(self.context.getRender2World().vw.toList(), [5, 6, 7, 1])

    # TODO: fix SceneContext.setRender2World (py_scene_rdl2_scene_context.cc):
    # the context stores a raw pointer to the Python-owned Mat4d without
    # keeping it alive (it needs with_custodian_and_ward<1, 2>), so passing a
    # temporary leaves getRender2World() reading freed memory.
    # def test_render_to_world_keeps_matrix_alive(self):
    #     self.context.setRender2World(scene_rdl2.Mat4d(
    #         [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [5, 6, 7, 1]]))
    #     garbage = [scene_rdl2.Mat4d([[9] * 4] * 4) for _ in range(1000)]
    #     self.assertEqual(self.context.getRender2World().vw.toList(), [5, 6, 7, 1])

    def test_no_primary_camera(self):
        self.assertIsNone(self.context.getPrimaryCamera())

    @requires_test_dsos
    def test_geometry_and_geometry_set_lists(self):
        self.context.createSceneObject("FakeTeapot", "teapot")
        self.context.createSceneObject("GeometrySet", "geoms")
        self.assertEqual(self.context.getGeometryListSize(), 1)
        self.assertEqual(self.context.getGeometryAt(0).getName(), "teapot")
        self.assertIsNone(self.context.getGeometryAt(1))
        self.assertEqual(self.context.getGeometrySetListSize(), 1)
        self.assertEqual(self.context.getGeometrySetAt(0).getName(), "geoms")
        self.assertIsNone(self.context.getGeometrySetAt(1))


if __name__ == "__main__":
    unittest.main()
