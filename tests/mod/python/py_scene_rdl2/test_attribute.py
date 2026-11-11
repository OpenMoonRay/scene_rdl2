# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestAttribute, using attributes of real
SceneClasses rather than directly constructed Attributes. See the bindings
README for the "Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import EXTENSIVE_OBJECT_DEFAULTS, Rdl2TestCase, make_context


class TestAttribute(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()
        self.scene_class = self.context.createSceneClass("ExtensiveObject")
        output_class = self.context.getSceneClass("RenderOutput")
        light_class = self.context.createSceneClass("FakeLight")
        self.constant = self.scene_class.getAttribute("bool")
        self.bindable = self.scene_class.getAttribute("string")
        self.blurrable = self.scene_class.getAttribute("float")
        self.enumerable = output_class.getAttribute("result")
        self.filename = light_class.getAttribute("texture")
        self.attributes = [self.constant, self.bindable, self.blurrable,
                           self.enumerable, self.filename]

    def set_metadata(self):
        for attribute in (self.constant, self.bindable, self.blurrable):
            attribute.setMetadata("description", attribute.getName() + " attribute")
            attribute.setMetadata("min", "0.0")
            attribute.setMetadata("max", "1.0")

    def test_get_name(self):
        # Mirrors TestAttribute::testGetName.
        self.assertEqual([a.getName() for a in self.attributes],
                         ["bool", "string", "float", "result", "texture"])

    def test_get_type(self):
        # Mirrors TestAttribute::testGetType.
        types = scene_rdl2.AttributeType
        self.assertEqual([a.getType() for a in self.attributes],
                         [types.BOOL, types.STRING, types.FLOAT, types.INT, types.STRING])

    def test_get_flags(self):
        # Mirrors TestAttribute::testGetFlags.
        # Omits: BINDABLE | BLURRABLE. No built-in or test SceneClass declares
        # an attribute with both flags, and Python cannot declare one.
        flags = scene_rdl2.AttributeFlags
        self.assertEqual([a.getFlags() for a in self.attributes],
                         [flags.NONE, flags.BINDABLE, flags.BLURRABLE,
                          flags.ENUMERABLE, flags.FILENAME])

    # TODO: bind Attribute.getDefaultValue (py_scene_rdl2_attribute.cc). Python
    # can return the value in the attribute's own type, so no type argument or
    # wrong-type error (which the C++ test also checks) is needed.
    # def test_get_default_value(self):
    #     # Mirrors TestAttribute::testGetDefaultValue.
    #     for name, expected in EXTENSIVE_OBJECT_DEFAULTS.items():
    #         with self.subTest(name):
    #             self.assertValuesAlmostEqual(
    #                 self.scene_class.getAttribute(name).getDefaultValue(), expected)

    def test_is_bindable(self):
        # Mirrors TestAttribute::testIsBindable.
        # Omits: BINDABLE | BLURRABLE, as in test_get_flags.
        self.assertEqual([a.isBindable() for a in self.attributes],
                         [False, True, False, False, False])

    def test_is_blurrable(self):
        # Mirrors TestAttribute::testIsBlurrable.
        # Omits: BINDABLE | BLURRABLE, as in test_get_flags.
        self.assertEqual([a.isBlurrable() for a in self.attributes],
                         [False, False, True, False, False])

    def test_is_enumerable(self):
        # Mirrors TestAttribute::testIsEnumerable.
        self.assertEqual([a.isEnumerable() for a in self.attributes],
                         [False, False, False, True, False])

    def test_is_filename(self):
        # Mirrors TestAttribute::testIsFilename.
        self.assertEqual([a.isFilename() for a in self.attributes],
                         [False, False, False, False, True])

    def test_set_metadata(self):
        # Mirrors TestAttribute::testSetMetadata.
        self.set_metadata()
        self.assertEqual(self.constant.getMetadata("min"), "0.0")

    def test_get_metadata(self):
        # Mirrors TestAttribute::testGetMetadata.
        self.set_metadata()
        for attribute in (self.constant, self.bindable, self.blurrable):
            with self.subTest(attribute.getName()):
                self.assertEqual(attribute.getMetadata("description"),
                                 attribute.getName() + " attribute")
                self.assertEqual(attribute.getMetadata("min"), "0.0")
                self.assertEqual(attribute.getMetadata("max"), "1.0")
                with self.assertRaises(ValueError):
                    attribute.getMetadata("default")

    def test_metadata_exists(self):
        # Mirrors TestAttribute::testMetadataExists.
        self.set_metadata()
        for attribute in (self.constant, self.bindable, self.blurrable):
            with self.subTest(attribute.getName()):
                for key in ("description", "min", "max"):
                    self.assertTrue(attribute.metadataExists(key))
                self.assertFalse(attribute.metadataExists("pizza"))
                self.assertFalse(attribute.metadataEmpty())

    def test_iterate_metadata(self):
        # Mirrors TestAttribute::testIterateMetadata. The ExtensiveObject
        # attributes also carry a "comment" entry the C++ fixtures do not.
        self.set_metadata()
        for attribute in (self.constant, self.bindable, self.blurrable):
            with self.subTest(attribute.getName()):
                self.assertEqual(attribute.getMetaDataKeys(),
                                 ["comment", "description", "max", "min"])
                metadata = attribute.getMetdaDataMap()
                self.assertEqual(sorted(metadata), ["comment", "description", "max", "min"])
                self.assertEqual(metadata["description"], attribute.getName() + " attribute")
                self.assertEqual(metadata["max"], "1.0")
                self.assertEqual(metadata["min"], "0.0")

    # TODO: fix the Attribute binding (py_scene_rdl2_attribute.cc): the metadata
    # map accessor is misspelled "getMetdaDataMap". test_iterate_metadata uses
    # that name, so update it too unless the old name is kept as an alias.
    # def test_metadata_map_spelling(self):
    #     self.assertEqual(self.constant.getMetadataMap(),
    #                      {"comment": "This is a boolean value."})

    def test_attribute_type(self):
        # Mirrors TestAttribute::testAttributeType, which maps C++ types to
        # AttributeType values at compile time. This checks the same mapping
        # through getType() and getTypeName() on an attribute of each type.
        # Omits: the Mat3 types (see the TODO below).
        for name in EXTENSIVE_OBJECT_DEFAULTS:
            with self.subTest(name):
                attribute = self.scene_class.getAttribute(name)
                self.assertEqual(attribute.getType(),
                                 getattr(scene_rdl2.AttributeType, name.upper()))
                self.assertEqual(attribute.getTypeName(),
                                 "".join(p[0].upper() + p[1:] for p in name.split("_")))
        geometries = self.context.getSceneClass("Layer").getAttribute("geometries")
        self.assertEqual(geometries.getType(), scene_rdl2.AttributeType.SCENE_OBJECT_INDEXABLE)

    # TODO: fix the AttributeType enum (py_scene_rdl2_enums.cc): it has no Mat3
    # values, and exposes TYPE_UNKNOWN under the name UNKNOWN_VEC.
    # def test_attribute_type_enum_values(self):
    #     # Mirrors TestAttribute::testAttributeType (the remainder).
    #     types = scene_rdl2.AttributeType
    #     for name in ("UNKNOWN", "MAT3F", "MAT3D", "MAT3F_VECTOR", "MAT3D_VECTOR"):
    #         self.assertTrue(hasattr(types, name), name)
    #     user_data_class = self.context.getSceneClass("UserData")
    #     self.assertEqual(user_data_class.getAttribute("mat3f_values_0").getType(),
    #                      types.MAT3F_VECTOR)

    def test_object_type(self):
        attribute = self.scene_class.getAttribute("scene_object")
        self.assertEqual(attribute.getObjectType(), scene_rdl2.SceneObjectInterface.GENERIC)
        self.assertEqual(attribute.getObjectTypeStr(), "SceneObject")

    # TODO: bind Attribute.getAliases (py_scene_rdl2_attribute.cc).
    # ExtensiveObject declares aliases such as "bool vector" for bool_vector.
    # No C++ test reads aliases directly.
    # def test_aliases(self):
    #     self.assertEqual(self.scene_class.getAttribute("bool_vector").getAliases(),
    #                      ["bool vector"])
    #     self.assertEqual(self.scene_class.getAttribute("bool").getAliases(), [])


class TestAttributeEnumValues(Rdl2TestCase):
    """RenderOutput's built-in "result" attribute is an enumerable Int, and
    "file_name" is not. Each context has its own SceneClass, so changing enum
    values here does not affect other tests."""

    def setUp(self):
        context = scene_rdl2.SceneContext()
        scene_class = context.createSceneObject("RenderOutput", "out").getSceneClass()
        self.attr = scene_class.getAttribute("result")
        self.other = scene_class.getAttribute("file_name")

    def test_set_enum_value(self):
        # Mirrors TestAttribute::testSetEnumValue.
        self.attr.setEnumValue(100, "hundred")
        self.assertEqual(self.attr.getEnumDescription(100), "hundred")
        self.attr.setEnumValue(100, "one hundred")
        self.assertEqual(self.attr.getEnumDescription(100), "one hundred")
        with self.assertRaises(RuntimeError):
            self.other.setEnumValue(0, "thing")

    def test_get_enum_description(self):
        # Mirrors TestAttribute::testGetEnumDescription.
        self.assertEqual(self.attr.getEnumDescription(0), "beauty")
        self.assertEqual(self.attr.getEnumDescription(1), "alpha")
        self.assertEqual(self.attr.getEnumDescription(2), "depth")
        with self.assertRaises(ValueError):
            self.attr.getEnumDescription(99999)
        with self.assertRaises(RuntimeError):
            self.other.getEnumDescription(0)

    # TODO: fix the Attribute binding (py_scene_rdl2_attribute.cc):
    # Attribute::isValidEnumValue is bound under the name "getEnumDescription"
    # (shadowed by the real getEnumDescription overload), so it is unreachable.
    # def test_is_valid_enum_value(self):
    #     # Mirrors TestAttribute::testIsValidEnumValue.
    #     self.assertTrue(self.attr.isValidEnumValue(0))
    #     self.assertTrue(self.attr.isValidEnumValue(1))
    #     self.assertFalse(self.attr.isValidEnumValue(99999))
    #     with self.assertRaises(RuntimeError):
    #         self.other.isValidEnumValue(0)

    def test_iterate_enum_values(self):
        # Mirrors TestAttribute::testIterateEnumValues.
        keys = self.attr.getEnumValKeys()
        self.assertEqual(keys[:3], [0, 1, 2])
        self.assertEqual(keys, sorted(keys))
        values = self.attr.getEnumValMap()
        self.assertEqual(sorted(values), keys)
        self.assertEqual([values[k] for k in keys[:3]], ["beauty", "alpha", "depth"])
        self.assertEqual(self.other.getEnumValKeys(), [])
        self.assertEqual(self.other.getEnumValMap(), {})


if __name__ == "__main__":
    unittest.main()
