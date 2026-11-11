# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestAttributeKey: the AttributeKey<T> bindings
(AttributeKeyBool, AttributeKeyFloat, ...). See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import Rdl2TestCase, make_context


# ExtensiveObject attribute -> AttributeKey class for its type.
KEY_CLASSES = {
    "bool": "AttributeKeyBool", "int": "AttributeKeyInt",
    "long": "AttributeKeyLong", "float": "AttributeKeyFloat",
    "double": "AttributeKeyDouble", "string": "AttributeKeyString",
    "rgb": "AttributeKeyRgb", "rgba": "AttributeKeyRgba",
    "vec2f": "AttributeKeyVec2f", "vec2d": "AttributeKeyVec2d",
    "vec3f": "AttributeKeyVec3f", "vec3d": "AttributeKeyVec3d",
    "vec4f": "AttributeKeyVec4f", "vec4d": "AttributeKeyVec4d",
    "mat4f": "AttributeKeyMat4f", "mat4d": "AttributeKeyMat4d",
    "bool_vector": "AttributeKeyBoolVector", "int_vector": "AttributeKeyIntVector",
    "long_vector": "AttributeKeyLongVector", "float_vector": "AttributeKeyFloatVector",
    "double_vector": "AttributeKeyDoubleVector",
    "string_vector": "AttributeKeyStringVector", "rgb_vector": "AttributeKeyRgbVector",
    "rgba_vector": "AttributeKeyRgbaVector", "vec2f_vector": "AttributeKeyVec2fVector",
    "vec2d_vector": "AttributeKeyVec2dVector", "vec3f_vector": "AttributeKeyVec3fVector",
    "vec3d_vector": "AttributeKeyVec3dVector", "vec4f_vector": "AttributeKeyVec4fVector",
    "vec4d_vector": "AttributeKeyVec4dVector", "mat4f_vector": "AttributeKeyMat4fVector",
    "mat4d_vector": "AttributeKeyMat4dVector",
    "scene_object_vector": "AttributeKeySceneObjectVector",
}

# Two attributes of the same type on one SceneClass, for key inequality.
DISTINCT_ATTRIBUTES = {
    "AttributeKeyBool": ("SceneVariables", "slerp_xforms", "disable_optimized_hair_sampling"),
    "AttributeKeyInt": ("SceneVariables", "image_width", "image_height"),
    "AttributeKeyFloat": ("SceneVariables", "min_frame", "max_frame"),
    "AttributeKeyString": ("UserData", "bool_key", "int_key"),
    "AttributeKeyRgb": ("FakeLight", "color", "saturation"),
    "AttributeKeyVec2f": ("FakeLight", "texture_translation", "texture_coverage"),
    "AttributeKeyIntVector": ("SceneVariables", "aperture_window", "region_window"),
    "AttributeKeyFloatVector": ("UserData", "float_values_0", "float_values_1"),
    "AttributeKeyStringVector": ("Metadata", "name", "type"),
    "AttributeKeyRgbVector": ("UserData", "color_values_0", "color_values_1"),
    "AttributeKeyVec2fVector": ("UserData", "vec2f_values_0", "vec2f_values_1"),
    "AttributeKeyVec3fVector": ("UserData", "vec3f_values_0", "vec3f_values_1"),
    "AttributeKeyMat4fVector": ("UserData", "mat4f_values_0", "mat4f_values_1"),
    "AttributeKeySceneObjectVector": ("Layer", "surface_shaders", "lightsets"),
}


class TestAttributeKey(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()
        self.scene_class = self.context.createSceneClass("ExtensiveObject")
        self.light_class = self.context.createSceneClass("FakeLight")
        self.output_class = self.context.getSceneClass("RenderOutput")

    def key(self, name):
        return getattr(scene_rdl2, KEY_CLASSES[name])(self.scene_class.getAttribute(name))

    def test_equality(self):
        # Mirrors TestAttributeKey::testEquality.
        # Omits: inequality for types with no two attributes on one test class
        # (e.g. Long, Double, Vec3d, Mat4f). Those check equality only.
        for name in KEY_CLASSES:
            with self.subTest(name):
                self.assertTrue(self.key(name) == self.key(name))
                self.assertFalse(self.key(name) != self.key(name))
        for key_class, (class_name, first, second) in DISTINCT_ATTRIBUTES.items():
            with self.subTest(key_class):
                scene_class = self.context.getSceneClass(class_name)
                key = getattr(scene_rdl2, key_class)(scene_class.getAttribute(first))
                other_key = getattr(scene_rdl2, key_class)(scene_class.getAttribute(second))
                self.assertFalse(key == other_key)
                self.assertTrue(key != other_key)

    def test_types(self):
        # Mirrors TestAttributeKey::testTypes.
        # Omits: SceneObject*, SceneObjectIndexable, and Mat3 keys (see the TODO
        # below). C++ rejects a TYPE_UNKNOWN attribute with TypeError; Python
        # cannot build one, so this uses an attribute of another type, which
        # raises RuntimeError.
        for name, key_class in KEY_CLASSES.items():
            with self.subTest(name):
                key = getattr(scene_rdl2, key_class)(self.scene_class.getAttribute(name))
                self.assertTrue(key.isValid())
                wrong_type = "int" if name == "bool" else "bool"
                with self.assertRaises(RuntimeError):
                    getattr(scene_rdl2, key_class)(self.scene_class.getAttribute(wrong_type))

    # TODO: bind the remaining AttributeKey types (py_scene_rdl2_attribute.cc):
    # TestAttributeKey::testTypes also covers SceneObject*, SceneObjectIndexable,
    # Mat3f, Mat3d, Mat3fVector, and Mat3dVector, which have no Python class.
    # def test_remaining_key_types(self):
    #     # Mirrors TestAttributeKey::testTypes (the remainder).
    #     key = scene_rdl2.AttributeKeySceneObject(self.scene_class.getAttribute("scene_object"))
    #     self.assertTrue(key.isValid())
    #     layer_class = self.context.getSceneClass("Layer")
    #     key = scene_rdl2.AttributeKeySceneObjectIndexable(layer_class.getAttribute("geometries"))
    #     self.assertTrue(key.isValid())
    #     user_data_class = self.context.getSceneClass("UserData")
    #     key = scene_rdl2.AttributeKeyMat3fVector(user_data_class.getAttribute("mat3f_values_0"))
    #     self.assertTrue(key.isValid())
    #     for name in ("AttributeKeyMat3f", "AttributeKeyMat3d", "AttributeKeyMat3dVector"):
    #         self.assertTrue(hasattr(scene_rdl2, name), name)

    def test_is_valid(self):
        # Mirrors TestAttributeKey::testIsValid.
        # Omits: an invalid key (see the TODO below).
        self.assertTrue(self.key("bool").isValid())

    # TODO: bind the AttributeKey default constructor (py_scene_rdl2_attribute.cc):
    # every key class requires an Attribute, so Python never sees an invalid key.
    # def test_default_key_is_invalid(self):
    #     # Mirrors TestAttributeKey::testIsValid (the remainder).
    #     self.assertFalse(scene_rdl2.AttributeKeyBool().isValid())

    def test_is_bindable(self):
        # Mirrors TestAttributeKey::testIsBindable.
        self.assertTrue(self.key("string").isBindable())
        self.assertFalse(self.key("bool").isBindable())

    def test_is_blurrable(self):
        # Mirrors TestAttributeKey::testIsBlurrable.
        self.assertTrue(self.key("float").isBlurrable())
        self.assertFalse(self.key("bool").isBlurrable())

    def test_is_enumerable(self):
        # Mirrors TestAttributeKey::testIsEnumerable.
        key = scene_rdl2.AttributeKeyInt(self.output_class.getAttribute("result"))
        self.assertTrue(key.isEnumerable())
        self.assertFalse(self.key("int").isEnumerable())

    def test_is_filename(self):
        # Mirrors TestAttributeKey::testIsFilename.
        key = scene_rdl2.AttributeKeyString(self.light_class.getAttribute("texture"))
        self.assertTrue(key.isFilename())
        self.assertFalse(self.key("string").isFilename())


if __name__ == "__main__":
    unittest.main()
