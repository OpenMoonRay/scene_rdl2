# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Mirrors tests/lib/scene/rdl2/TestSceneObject, and also covers the to*() casts.
See the bindings README for the "Mirrors" and "Omits" comments."""

import unittest

import scene_rdl2
from rdl2_test_util import EXTENSIVE_OBJECT_DEFAULTS, Rdl2TestCase, make_context, names


# Test DSO class -> (to*() cast that should succeed, Python type it returns,
# type name from getTypeName()).
CASTS = {
    "FakeTeapot": ("toGeometry", "Geometry",
                   "GENERIC (SceneObject) | NODE | GEOMETRY"),
    "FakeLight": ("toLight", "Light", "GENERIC (SceneObject) | NODE | LIGHT"),
    "FakeMaterial": ("toMaterial", "Material",
                     "GENERIC (SceneObject) | SHADER | ROOTSHADER | MATERIAL"),
    "FakeDisplacement": ("toDisplacement", "Displacement",
                         "GENERIC (SceneObject) | SHADER | ROOTSHADER | DISPLACEMENT"),
}

BUILTIN_CASTS = {
    "GeometrySet": ("toGeometrySet", "GeometrySet"),
    "LightSet": ("toLightSet", "LightSet"),
    "Layer": ("toLayer", "Layer"),
    "UserData": ("toUserData", "UserData"),
    "Metadata": ("toMetadata", "Metadata"),
    "RenderOutput": ("toRenderOutput", "RenderOutput"),
}

ALL_CASTS = sorted({cast for cast, _ in BUILTIN_CASTS.values()} |
                   {cast for cast, _, _ in CASTS.values()} |
                   {"toCamera", "toEnvMap", "toMap", "toNormalMap", "toLightFilter"})

RAMP4 = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]

# Values to set on each attribute, and the value get() should return. set()
# takes vectors, colors, and matrices as lists or tuples; matrices are flat,
# row-major lists of 16 values.
SET_VALUES = {
    "bool": False,
    "int": 7,
    "long": 2 ** 40,
    "float": 2.5,
    "double": 3.25,
    "string": "hello",
    "rgb": [1.0, 0.5, 0.25],
    "rgba": (1.0, 0.5, 0.25, 0.125),
    "vec2f": [5.0, 6.0],
    "vec2d": (7.0, 8.0),
    "vec3f": [1.0, 2.0, 3.5],
    "vec3d": [9.0, 8.0, 7.0],
    "vec4f": [1.0, 2.0, 3.0, 4.0],
    "vec4d": [4.0, 3.0, 2.0, 1.0],
    "mat4f": [float(i) for i in range(16)],
    "mat4d": tuple(float(i) for i in range(16, 32)),
    "bool_vector": [False, True, True],
    "int_vector": [1, 2, 3],
    "long_vector": [2 ** 40, 5],
    "float_vector": [0.5, 1.5],
    "double_vector": (0.25,),
    "string_vector": ["x", "y", "z"],
    "rgb_vector": [[1, 2, 3], [4, 5, 6]],
    "rgba_vector": [(1, 2, 3, 4)],
    "vec2f_vector": [[1, 2]],
    "vec2d_vector": [[1, 2]],
    "vec3f_vector": [[1, 2, 3]],
    "vec3d_vector": [[1, 2, 3]],
    "vec4f_vector": [[1, 2, 3, 4]],
    "vec4d_vector": [[1, 2, 3, 4]],
    "mat4f_vector": [list(range(16))],
    "mat4d_vector": [list(range(16))],
}

GET_TYPES = {
    "rgb": "Rgb", "rgba": "Rgba", "vec2f": "Vec2f", "vec2d": "Vec2d",
    "vec3f": "Vec3f", "vec3d": "Vec3d", "vec4f": "Vec4f", "vec4d": "Vec4d",
    "mat4f": "Mat4f", "mat4d": "Mat4d", "bool_vector": "BoolVector",
    "int_vector": "IntVector", "long_vector": "LongVector",
    "float_vector": "FloatVector", "double_vector": "DoubleVector",
    "string_vector": "StringVector", "rgb_vector": "RgbVector",
    "rgba_vector": "RgbaVector", "vec2f_vector": "Vec2fVector",
    "vec2d_vector": "Vec2dVector", "vec3f_vector": "Vec3fVector",
    "vec3d_vector": "Vec3dVector", "vec4f_vector": "Vec4fVector",
    "vec4d_vector": "Vec4dVector", "mat4f_vector": "Mat4fVector",
    "mat4d_vector": "Mat4dVector",
}


def rows(flat):
    return [list(flat[r * 4:r * 4 + 4]) for r in range(4)]


def expected_after_set(name):
    """get() returns matrices as rows, unlike the flat lists set() takes."""
    value = SET_VALUES[name]
    if name in ("mat4f", "mat4d"):
        return rows(value)
    if name in ("mat4f_vector", "mat4d_vector"):
        return [rows(m) for m in value]
    return value


class TestSceneObject(Rdl2TestCase):

    def setUp(self):
        self.context = make_context()
        self.obj = self.context.createSceneObject("ExtensiveObject", "obj")

    def values(self, name):
        return self.obj.get(name, 0), self.obj.get(name, 1)

    def delta_text(self):
        writer = scene_rdl2.AsciiWriter(self.context)
        writer.setDeltaEncoding(True)
        return writer.toString()

    def test_timestep_gets_and_sets(self):
        # Mirrors TestSceneObject::testTimestepGetsAndSets.
        # Omits: setting float_vector at a timestep (see the TODO below).

        # A non-blurrable attribute holds one value, whichever timestep is set.
        self.assertEqual(self.values("bool"), (True, True))
        self.obj.set("bool", False, 0)
        self.assertEqual(self.values("bool"), (False, False))
        self.obj.set("bool", True, 1)
        self.assertEqual(self.values("bool"), (True, True))

        # A blurrable attribute holds one value per timestep.
        self.assertEqual(self.values("int"), (42, 42))
        self.obj.set("int", 5, 0)
        self.assertEqual(self.values("int"), (5, 42))
        self.obj.set("int", 6, 1)
        self.assertEqual(self.values("int"), (5, 6))

        default = scene_rdl2.Rgb(0.1, 0.2, 0.3)
        begin = scene_rdl2.Rgb(0.4, 0.5, 0.6)
        end = scene_rdl2.Rgb(0.7, 0.8, 0.9)
        self.assertEqual(self.values("rgb"), (default, default))
        self.obj.set("rgb", [0.4, 0.5, 0.6], 0)
        self.assertEqual(self.values("rgb"), (begin, default))
        self.obj.set("rgb", [0.7, 0.8, 0.9], 1)
        self.assertEqual(self.values("rgb"), (begin, end))

        self.assertEqual(self.obj.get("float_vector", 0).toList(), [1.0, 2.0])
        self.assertEqual(self.obj.get("float_vector", 1).toList(), [1.0, 2.0])

    # TODO: fix SceneObject.set() with a timestep for vector attributes
    # (extractAndSetAttributeValueAtTimestep in py_scene_rdl2_helpers.cc): it
    # raises "Attribute type for 'float_vector' is not supported by the timestep
    # setter", though C++ allows it and get() accepts a timestep there.
    # def test_vector_attribute_at_timestep(self):
    #     # Mirrors TestSceneObject::testTimestepGetsAndSets (the remainder).
    #     self.obj.set("float_vector", [9.0], 0)
    #     self.assertEqual(self.obj.get("float_vector", 0).toList(), [9.0])
    #     self.assertEqual(self.obj.get("float_vector", 1).toList(), [9.0])
    #     self.obj.set("float_vector", [8.0], 1)
    #     self.assertEqual(self.obj.get("float_vector", 0).toList(), [8.0])
    #     self.assertEqual(self.obj.get("float_vector", 1).toList(), [8.0])

    def test_simple_gets_and_sets(self):
        # Mirrors TestSceneObject::testSimpleGetsAndSets.
        self.assertTrue(self.obj.get("bool"))
        self.obj.set("bool", False)
        self.assertFalse(self.obj.get("bool"))

        # Without a timestep, set() writes both timesteps.
        self.assertEqual(self.obj.get("int"), 42)
        self.obj.set("int", 7)
        self.assertEqual(self.obj.get("int"), 7)
        self.assertEqual(self.obj.get("int", 0), 7)
        self.assertEqual(self.obj.get("int", 1), 7)

        self.assertEqual(self.obj.get("rgb"), scene_rdl2.Rgb(0.1, 0.2, 0.3))
        self.obj.set("rgb", [0.4, 0.5, 0.6])
        self.assertEqual(self.obj.get("rgb"), scene_rdl2.Rgb(0.4, 0.5, 0.6))
        self.assertEqual(self.obj.get("rgb", 0), scene_rdl2.Rgb(0.4, 0.5, 0.6))
        self.assertEqual(self.obj.get("rgb", 1), scene_rdl2.Rgb(0.4, 0.5, 0.6))

        self.assertEqual(self.obj.get("float_vector").toList(), [1.0, 2.0])
        self.obj.set("float_vector", [0.5, 1.5])
        self.assertEqual(self.obj.get("float_vector").toList(), [0.5, 1.5])

    def test_convenience_gets_and_sets(self):
        # Mirrors TestSceneObject::testConvenienceGetsAndSets.
        # Omits: its gets and sets, which C++ makes by name rather than by
        # AttributeKey. Python only has the by-name form, so the two tests
        # above already make them. Also get<String>("bool") raising TypeError:
        # Python's get() is not typed; it returns the attribute's own type.
        with self.assertRaises(ValueError):
            self.obj.get("not an attribute")
        with self.assertRaises(ValueError):
            self.obj.set("not an attribute", True)
        with self.assertRaises(TypeError):
            self.obj.set("bool", "string value")
        with self.assertRaises(ValueError):
            self.obj.get("not an attribute", 0)
        with self.assertRaises(ValueError):
            self.obj.set("not an attribute", True, 0)
        with self.assertRaises(TypeError):
            self.obj.set("bool", "string value", 0)

    def test_reset_to_default(self):
        # Mirrors TestSceneObject::testResetToDefault.
        # Omits: the AttributeKey overload, which is not bound. Python resets by
        # name only.
        self.obj.set("int", 9001)
        self.obj.set("string", "hello")
        self.obj.set("long", 9002)
        self.obj.beginUpdate()
        self.obj.resetToDefault("int")
        self.obj.resetToDefault("string")
        self.obj.endUpdate()
        self.assertEqual(self.obj.get("int"), 42)
        self.assertEqual(self.obj.get("string"), "pizza")
        self.assertEqual(self.obj.get("long"), 9002)
        with self.assertRaises(RuntimeError):
            self.obj.resetToDefault("int")

    def test_reset_all_to_default(self):
        # Mirrors TestSceneObject::testResetAllToDefault.
        self.obj.set("int", 9001)
        self.obj.set("string", "hello")
        self.obj.set("long", 9002)
        self.obj.beginUpdate()
        self.obj.resetAllToDefault()
        self.obj.endUpdate()
        self.assertEqual(self.obj.get("int"), 42)
        self.assertEqual(self.obj.get("string"), "pizza")
        self.assertEqual(self.obj.get("long"), 43)
        with self.assertRaises(RuntimeError):
            self.obj.resetAllToDefault()

    def test_attribute_set_mask(self):
        # Mirrors TestSceneObject::testAttributeSetMask.
        # The C++ test reads mAttributeSetMask directly. Delta-encoded output
        # holds exactly the attributes whose bit is set, so this reads the mask
        # through AsciiWriter (see also the isAttributeSet TODO below).
        def assert_mask(expected):
            text = self.delta_text()
            for attribute in ('["int"]', '["string"]'):
                (self.assertIn if expected else self.assertNotIn)(attribute, text)

        assert_mask(False)
        self.obj.beginUpdate()
        self.obj.resetToDefault("int")
        self.obj.resetToDefault("string")
        self.obj.endUpdate()
        assert_mask(False)

        self.obj.set("int", 9001)
        self.obj.set("string", "hello")
        assert_mask(True)
        self.obj.commitChanges()
        assert_mask(False)

        # Setting the same value again is not a change.
        self.obj.set("int", 9001)
        self.obj.set("string", "hello")
        assert_mask(False)

        self.obj.beginUpdate()
        self.obj.resetToDefault("int")
        self.obj.resetToDefault("string")
        self.obj.endUpdate()
        assert_mask(True)

    # TODO: bind SceneObject.isAttributeSet (py_scene_rdl2_scene_object.cc),
    # the public accessor for the set mask. SceneObject.hasChanged is not a
    # substitute: it reads a separate update mask, which starts fully set on a
    # new object and is only reset by resetUpdate().
    # def test_is_attribute_set(self):
    #     # Mirrors TestSceneObject::testAttributeSetMask.
    #     def is_set(name):
    #         return self.obj.isAttributeSet(self.obj.getSceneClass().getAttribute(name))
    #     self.assertFalse(is_set("int"))
    #     self.obj.set("int", 9001)
    #     self.assertTrue(is_set("int"))
    #     self.obj.commitChanges()
    #     self.assertFalse(is_set("int"))
    #     self.obj.set("int", 9001)
    #     self.assertFalse(is_set("int"))

    def test_bindings(self):
        # Mirrors TestSceneObject::testBindings.
        target = self.context.createSceneObject("ExtensiveObject", "target")
        self.assertIsNone(self.obj.getBinding("string"))
        self.obj.setBinding("string", target)
        self.assertEqual(self.obj.getBinding("string").getName(), "target")
        with self.assertRaises(RuntimeError):
            self.obj.setBinding("float", target)
        with self.assertRaises(RuntimeError):
            self.obj.getBinding("float")

        self.obj.setBinding("string", None)
        self.assertIsNone(self.obj.getBinding("string"))

    # TODO: fix SceneObject.set() and setBinding() (py_scene_rdl2_helpers.cc,
    # py_scene_rdl2_scene_object.cc): each opens its own UpdateGuard, so calling
    # them between beginUpdate() and endUpdate() -- as the setBinding docstring
    # suggests for batching -- fails the "!mUpdateActive" assertion and aborts
    # the interpreter. Meanwhile resetToDefault() and the RenderOutput setters
    # require an explicit update, so callers must know which kind each is. The
    # C++ tests make all of these calls inside an update.
    # def test_set_inside_explicit_update(self):
    #     target = self.context.createSceneObject("ExtensiveObject", "target")
    #     self.obj.beginUpdate()
    #     self.obj.set("int", 1)
    #     self.obj.setBinding("string", target)
    #     self.obj.endUpdate()
    #     self.assertEqual(self.obj.get("int"), 1)
    #     self.assertEqual(self.obj.getBinding("string").getName(), "target")

    def test_attribute_names_and_types(self):
        names_and_types = self.obj.getAttributeNamesAndTypes()
        scene_class = self.obj.getSceneClass()
        self.assertEqual(names_and_types,
                         {name: scene_class.getAttribute(name).getTypeName()
                          for name in EXTENSIVE_OBJECT_DEFAULTS})
        self.assertEqual(names_and_types["mat4d_vector"], "Mat4dVector")
        self.assertEqual(self.obj.getAttributeNames(), list(EXTENSIVE_OBJECT_DEFAULTS))
        self.assertEqual(self.obj.getAttributeCount(), len(EXTENSIVE_OBJECT_DEFAULTS))
        self.assertEqual(self.obj.getAttributeAt(0).getName(), "bool")
        self.assertEqual(self.obj.getAttributeNamesAndIndices()["long"], 2)

    def test_defaults(self):
        for name, expected in EXTENSIVE_OBJECT_DEFAULTS.items():
            with self.subTest(name):
                self.assertValuesAlmostEqual(self.obj.get(name), expected)

    def test_get_return_types(self):
        for name, type_name in GET_TYPES.items():
            with self.subTest(name):
                self.assertIsInstance(self.obj.get(name), getattr(scene_rdl2, type_name))
        self.assertIsInstance(self.obj.get("int"), int)
        self.assertIsInstance(self.obj.get("double"), float)
        self.assertIsInstance(self.obj.get("string"), str)
        self.assertEqual(type(self.obj.get("scene_object_vector")).__name__,
                         "SceneObjectVector")

    # TODO: fix the SceneObjectVector bindings: py_scene_rdl2_types.cc (the
    # wrapper get() returns) and py_scene_rdl2_scene_object.cc (an indexing
    # suite over rdl2::SceneObjectVector) both register a class named
    # "SceneObjectVector", so the module attribute is not the type get() returns.
    # def test_scene_object_vector_type(self):
    #     self.assertIsInstance(self.obj.get("scene_object_vector"),
    #                           scene_rdl2.SceneObjectVector)

    def test_set_and_get_every_type(self):
        for name in SET_VALUES:
            with self.subTest(name):
                self.obj.set(name, SET_VALUES[name])
                self.assertValuesAlmostEqual(self.obj.get(name), expected_after_set(name))

    def test_set_int_into_float(self):
        self.obj.set("float", 3)
        self.assertEqual(self.obj.get("float"), 3.0)

    def test_scene_object_attributes(self):
        other = self.context.createSceneObject("ExtensiveObject", "other")
        self.obj.set("scene_object", other)
        self.assertEqual(self.obj.get("scene_object").getName(), "other")
        self.obj.set("scene_object", None)
        self.assertIsNone(self.obj.get("scene_object"))

        self.obj.set("scene_object_vector", [other, self.obj])
        self.assertEqual(names(self.obj.get("scene_object_vector").toList()),
                         ["other", "obj"])

    def test_float_into_int_raises(self):
        with self.assertRaises(TypeError):
            self.obj.set("int", 3.5)
        self.assertEqual(self.obj.get("int"), 42)

    def test_wrong_size_raises(self):
        with self.assertRaises(IndexError):
            self.obj.set("vec3f", [1.0, 2.0])
        with self.assertRaises(ValueError):
            self.obj.set("mat4f", [1.0, 2.0, 3.0])
        with self.assertRaises(ValueError):
            self.obj.set("mat4f", RAMP4)
        with self.assertRaises(TypeError):
            self.obj.set("mat4f", scene_rdl2.Mat4f(RAMP4))

    def test_set_primitive_vector_rejects_container_objects(self):
        with self.assertRaises(RuntimeError):
            self.obj.set("int_vector", self.obj.get("int_vector"))

    # TODO: fix SceneObject.set() for vector and color attributes
    # (internal_setVecAttrValue in py_scene_rdl2_helpers.cc): a Vec3f/Rgb/...
    # object is neither a list nor a tuple, so set() silently stores an
    # uninitialized value instead of converting it or raising TypeError.
    # def test_set_vector_attribute_from_math_object(self):
    #     self.obj.set("vec3f", scene_rdl2.Vec3f(4, 5, 6))
    #     self.assertEqual(self.obj.get("vec3f").toList(), [4.0, 5.0, 6.0])
    #     self.obj.set("rgb", scene_rdl2.Rgb(0.5, 0.25, 0.125))
    #     self.assertEqual(self.obj.get("rgb").toList(), [0.5, 0.25, 0.125])

    def test_timestep_defaults_and_enum(self):
        # get() without a timestep returns the TIMESTEP_BEGIN value.
        self.obj.set("float", 9.0, 1)
        self.assertEqual(self.obj.get("float"), 1.0)

        self.obj.set("int", 5, scene_rdl2.AttributeTimestep.TIMESTEP_END)
        self.assertEqual(self.obj.get("int", scene_rdl2.AttributeTimestep.TIMESTEP_BEGIN), 42)
        self.assertEqual(self.obj.get("int", scene_rdl2.AttributeTimestep.TIMESTEP_END), 5)

    def test_vector_and_matrix_timesteps(self):
        self.obj.set("vec3f", [7, 8, 9], 1)
        self.assertEqual(self.obj.get("vec3f", 1).toList(), [7.0, 8.0, 9.0])
        self.assertEqual(self.obj.get("vec3f", 0).toList(), [1.0, 2.0, 3.0])
        self.obj.set("mat4d", [float(i) for i in range(16)], 1)
        self.assertEqual(self.obj.get("mat4d", 1).toList(), RAMP4)

    def test_invalid_timestep_raises(self):
        with self.assertRaises(ValueError):
            self.obj.get("float", 2)
        with self.assertRaises(RuntimeError):
            self.obj.set("float", 1.0, 2)

    def test_mark_attribute_changed(self):
        self.context.commitAllChanges()
        self.assertNotIn('["int"]', self.delta_text())
        self.obj.markAttributeChanged("int")
        self.assertIn('["int"]', self.delta_text())

    def test_casts_and_type_names(self):
        for class_name, (cast, type_name, full_type_name) in CASTS.items():
            with self.subTest(class_name):
                obj = self.context.createSceneObject(class_name, class_name.lower())
                self.assertEqual(obj.getTypeName(), full_type_name)
                self.assertIsInstance(getattr(obj, cast)(), getattr(scene_rdl2, type_name))
                for other in ALL_CASTS:
                    if other != cast:
                        self.assertIsNone(getattr(obj, other)(), other)

    def test_node_and_shader_casts(self):
        teapot = self.context.createSceneObject("FakeTeapot", "teapot")
        self.assertIsInstance(teapot.toNode(), scene_rdl2.Node)
        material = self.context.createSceneObject("FakeMaterial", "material")
        self.assertIsNone(material.toNode())

    def test_generic_object(self):
        obj = self.context.createSceneObject("ExampleObject", "example")
        self.assertEqual(obj.getType(), scene_rdl2.SceneObjectInterface.GENERIC)
        self.assertIsNone(obj.toGeometry())


class TestBuiltinSceneObjects(Rdl2TestCase):
    """SceneObject behavior that needs no DSOs."""

    def setUp(self):
        self.context = scene_rdl2.SceneContext()

    def test_get_class(self):
        # Mirrors TestSceneObject::testGetClass.
        obj = self.context.createSceneObject("UserData", "/scene/data")
        self.assertIsInstance(obj, scene_rdl2.SceneObject)
        self.assertEqual(obj.getSceneClass().getName(), "UserData")

    def test_get_name(self):
        # Mirrors TestSceneObject::testGetName.
        obj = self.context.createSceneObject("UserData", "/scene/data")
        self.assertEqual(obj.getName(), "/scene/data")

    def test_get_type(self):
        obj = self.context.createSceneObject("UserData", "/scene/data")
        # getType() returns a bitmask of every interface the object implements.
        interfaces = scene_rdl2.SceneObjectInterface
        self.assertEqual(int(obj.getType()),
                         int(interfaces.GENERIC) | int(interfaces.USERDATA))

    def test_casts(self):
        for class_name, (cast, type_name) in BUILTIN_CASTS.items():
            with self.subTest(class_name):
                obj = self.context.createSceneObject(class_name, class_name.lower())
                self.assertIsInstance(getattr(obj, cast)(), getattr(scene_rdl2, type_name))
                for other in ALL_CASTS:
                    if other != cast:
                        self.assertIsNone(getattr(obj, other)(), other)


if __name__ == "__main__":
    unittest.main()
