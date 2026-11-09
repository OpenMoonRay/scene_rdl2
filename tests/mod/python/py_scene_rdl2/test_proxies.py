# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestProxies. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import (Rdl2TestCase, make_context, read_scene, requires_test_dsos,
                            write_scene)


@requires_test_dsos
class TestProxies(Rdl2TestCase):
    """The LibLaden* DSOs call into a library that does not exist, so they can
    only be instantiated as proxies."""

    # Test DSO class -> (Python type of the proxy, to*() cast that succeeds).
    PROXIES = {
        "LibLadenCamera": ("CameraProxy", "toCamera"),
        "LibLadenEnvMap": ("EnvMapProxy", "toEnvMap"),
        "LibLadenGeometry": ("GeometryProxy", "toGeometry"),
        "LibLadenLight": ("LightProxy", "toLight"),
        "LibLadenMap": ("MapProxy", "toMap"),
        "LibLadenNormalMap": ("NormalMapProxy", "toNormalMap"),
        "LibLadenMaterial": ("MaterialProxy", "toMaterial"),
        "LibLadenDwaBaseLayerable": ("DwaBaseLayerableProxy", "toMaterial"),
    }

    def setUp(self):
        self.context = make_context(proxy_mode=True)

    def round_trip(self):
        path = self.temp_path("proxies.rdlb")
        write_scene(self.context, path)
        verify = make_context(proxy_mode=True)
        read_scene(verify, path)
        return verify

    def check_library_ladenness(self, class_name):
        name = "/seq/shot/" + class_name
        obj = self.context.createSceneObject(class_name, name)
        self.assertEqual(obj.get("library_ladenness"), 9001)
        obj.set("library_ladenness", 42)

        verify = self.round_trip().getSceneObject(name)
        self.assertEqual(verify.getSceneClass().getName(), class_name)
        self.assertEqual(verify.get("library_ladenness"), 42)

    def test_proxy_dwa_base_layerable(self):
        # Mirrors TestProxies::testProxyDwaBaseLayerable.
        mat = self.context.createSceneObject("LibLadenDwaBaseLayerable", "/seq/shot/layerMat")
        mat_a = self.context.createSceneObject("LibLadenDwaBaseLayerable", "/seq/shot/layerMatA")
        mat.set("mat_a", mat_a)

        verify = self.round_trip()
        verify_mat = verify.getSceneObject("/seq/shot/layerMat")
        self.assertIsNotNone(verify_mat.toMaterial())
        self.assertIsNotNone(verify.getSceneObject("/seq/shot/layerMatA").toMaterial())
        self.assertEqual(verify_mat.get("mat_a").getName(), "/seq/shot/layerMatA")

    def test_proxy_camera(self):
        # Mirrors TestProxies::testProxyCamera.
        self.check_library_ladenness("LibLadenCamera")

    def test_proxy_display_filter(self):
        # Mirrors TestProxies::testProxyDisplayFilter.
        # Omits: casting the proxy to its own type (see the TODO below).
        self.check_library_ladenness("LibLadenDisplayFilter")

    def test_proxy_env_map(self):
        # Mirrors TestProxies::testProxyEnvMap.
        self.check_library_ladenness("LibLadenEnvMap")

    def test_proxy_geometry(self):
        # Mirrors TestProxies::testProxyGeometry.
        self.check_library_ladenness("LibLadenGeometry")

    def test_proxy_light(self):
        # Mirrors TestProxies::testProxyLight.
        self.check_library_ladenness("LibLadenLight")

    def test_proxy_light_filter(self):
        # Mirrors TestProxies::testProxyLightFilter.
        # Omits: casting the proxy to its own type (see the TODO below).
        self.check_library_ladenness("LibLadenLightFilter")

    def test_proxy_map(self):
        # Mirrors TestProxies::testProxyMap.
        self.check_library_ladenness("LibLadenMap")

    def test_proxy_normal_map(self):
        # Mirrors TestProxies::testProxyNormalMap.
        self.check_library_ladenness("LibLadenNormalMap")

    def test_proxy_material(self):
        # Mirrors TestProxies::testProxyMaterial.
        self.check_library_ladenness("LibLadenMaterial")

    def test_proxy_types_and_casts(self):
        for class_name, (proxy_type, cast) in self.PROXIES.items():
            with self.subTest(class_name):
                obj = self.context.createSceneObject(class_name, "/seq/shot/" + class_name)
                self.assertIsInstance(obj, getattr(scene_rdl2, proxy_type))
                self.assertIsNotNone(getattr(obj, cast)())

    def test_proxy_casts_reject_other_types(self):
        camera = self.context.createSceneObject("LibLadenCamera", "camera")
        self.assertIsNone(camera.toGeometry())

    # TODO: bind proxies for LightFilter and DisplayFilter
    # (py_scene_rdl2_proxies.cc, py_scene_rdl2_helpers.cc), and a DisplayFilter
    # class with SceneObject.toDisplayFilter(). Both come back as plain
    # SceneObjects whose getTypeName() reports "UNKNOWN".
    # def test_filter_proxy_types(self):
    #     # Mirrors TestProxies::testProxyLightFilter and
    #     # TestProxies::testProxyDisplayFilter (the remainder).
    #     light_filter = self.context.createSceneObject("LibLadenLightFilter", "light_filter")
    #     self.assertIsInstance(light_filter.toLightFilter(), scene_rdl2.LightFilter)
    #     self.assertNotIn("UNKNOWN", light_filter.getTypeName())
    #     display_filter = self.context.createSceneObject("LibLadenDisplayFilter", "display_filter")
    #     self.assertIsInstance(display_filter.toDisplayFilter(), scene_rdl2.DisplayFilter)
    #     self.assertNotIn("UNKNOWN", display_filter.getTypeName())


if __name__ == "__main__":
    unittest.main()
