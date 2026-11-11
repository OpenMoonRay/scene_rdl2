# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestSceneClass. See the bindings README for the
"Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import EXTENSIVE_OBJECT_DEFAULTS, Rdl2TestCase, make_context


class TestSceneClass(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()
        self.scene_class = self.context.createSceneClass("ExtensiveObject")

    def test_get_name(self):
        # Mirrors TestSceneClass::testGetName.
        self.assertEqual(self.scene_class.getName(), "ExtensiveObject")

    # TODO: bind SceneClass.getAttribute(key) (py_scene_rdl2_scene_class.cc):
    # only the by-name overload is bound, so a Python AttributeKey cannot be
    # used to look anything up.
    # def test_get_attribute_by_key(self):
    #     # Mirrors TestSceneClass::testGetAttributeByKey.
    #     for key_class, name, type_value, flags in (
    #             (scene_rdl2.AttributeKeyBool, "bool",
    #              scene_rdl2.AttributeType.BOOL, scene_rdl2.AttributeFlags.NONE),
    #             (scene_rdl2.AttributeKeyString, "string",
    #              scene_rdl2.AttributeType.STRING, scene_rdl2.AttributeFlags.BINDABLE),
    #             (scene_rdl2.AttributeKeyFloat, "float",
    #              scene_rdl2.AttributeType.FLOAT, scene_rdl2.AttributeFlags.BLURRABLE)):
    #         key = key_class(self.scene_class.getAttribute(name))
    #         attribute = self.scene_class.getAttribute(key)
    #         self.assertEqual(attribute.getName(), name)
    #         self.assertEqual(attribute.getType(), type_value)
    #         self.assertEqual(attribute.getFlags(), flags)

    def test_get_attribute_by_name(self):
        # Mirrors TestSceneClass::testGetAttributeByName.
        flags = scene_rdl2.AttributeFlags
        types = scene_rdl2.AttributeType
        for name, attribute_type, attribute_flags in (("bool", types.BOOL, flags.NONE),
                                                      ("string", types.STRING, flags.BINDABLE),
                                                      ("float", types.FLOAT, flags.BLURRABLE)):
            attribute = self.scene_class.getAttribute(name)
            self.assertEqual(attribute.getName(), name)
            self.assertEqual(attribute.getType(), attribute_type)
            self.assertEqual(attribute.getFlags(), attribute_flags)
        with self.assertRaises(ValueError):
            self.scene_class.getAttribute("no_such_attribute")

    # TODO: bind SceneClass.getAttributeKey (py_scene_rdl2_scene_class.cc notes
    # it as unbound). Python would need no type argument: getAttributeKey(name)
    # can return the matching AttributeKey* class.
    # def test_get_attribute_key_by_name(self):
    #     # Mirrors TestSceneClass::testGetAttributeKeyByName.
    #     key = self.scene_class.getAttributeKey("float")
    #     self.assertIsInstance(key, scene_rdl2.AttributeKeyFloat)
    #     self.assertTrue(key == scene_rdl2.AttributeKeyFloat(
    #         self.scene_class.getAttribute("float")))

    def test_iterate_attributes(self):
        # Mirrors TestSceneClass::testIterateAttributes.
        names = list(EXTENSIVE_OBJECT_DEFAULTS)
        self.assertEqual(self.scene_class.getAttributeNames(), names)
        self.assertEqual(self.scene_class.getAttributeCount(), len(names))
        self.assertEqual([self.scene_class.getAttributeAt(i).getName()
                          for i in range(len(names))], names)

    # TODO: fix the SceneClass.declare*Attr bindings (py_scene_rdl2_scene_class.cc):
    # each is registered through a C-style cast that turns its bp::list aliases
    # parameter into std::vector<std::string>, which Python cannot supply, so
    # every call fails with ArgumentError. Fixed, declaring on a completed
    # SceneClass should raise RuntimeError, as in C++. This is not a mirror of
    # TestSceneClass's testDeclare* tests, which need an incomplete SceneClass.
    # def test_declare_on_complete_class_raises(self):
    #     with self.assertRaises(RuntimeError):
    #         self.scene_class.declareIntAttr("new_attribute", 5,
    #                                         scene_rdl2.AttributeFlags.NONE,
    #                                         scene_rdl2.SceneObjectInterface.GENERIC, [])


if __name__ == "__main__":
    unittest.main()
