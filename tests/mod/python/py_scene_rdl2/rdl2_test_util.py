# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

"""Shared helpers for the scene_rdl2 Python binding tests.

The tests import the scene_rdl2 module found on PYTHONPATH. Tests that need
SceneClasses beyond the built-in ones use the test DSOs built for the C++
scene_rdl2 unit tests (ExtensiveObject, FakeTeapot, LibLadenCamera, ...),
located through the SCENE_RDL2_TEST_DSO_PATH environment variable. CTest sets
both; when running by hand, importing this module fails if
SCENE_RDL2_TEST_DSO_PATH does not name a directory, so that the DSO-based tests
cannot quietly go unrun.
"""

import os
import tempfile
import unittest

import scene_rdl2

TEST_DSO_PATH = os.environ.get("SCENE_RDL2_TEST_DSO_PATH", "")

if not os.path.isdir(TEST_DSO_PATH):
    raise RuntimeError("SCENE_RDL2_TEST_DSO_PATH must name the directory of "
                       "scene_rdl2 test DSOs, but is %r" % TEST_DSO_PATH)

# Every attribute ExtensiveObject declares, with its default value as returned
# by get() and converted to plain Python values by to_python().
EXTENSIVE_OBJECT_DEFAULTS = {
    "bool": True,
    "int": 42,
    "long": 43,
    "float": 1.0,
    "double": 2.0,
    "string": "pizza",
    "rgb": [0.1, 0.2, 0.3],
    "rgba": [0.1, 0.2, 0.3, 0.4],
    "vec2f": [1.0, 2.0],
    "vec2d": [2.0, 3.0],
    "vec3f": [1.0, 2.0, 3.0],
    "vec3d": [2.0, 3.0, 4.0],
    "vec4f": [1.0, 2.0, 3.0, 4.0],
    "vec4d": [2.0, 3.0, 4.0, 5.0],
    "mat4f": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
              [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]],
    "mat4d": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
              [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]],
    "scene_object": None,
    "bool_vector": [True, False],
    "int_vector": [100, 101],
    "long_vector": [102, 103],
    "float_vector": [1.0, 2.0],
    "double_vector": [3.0, 4.0],
    "string_vector": ["a", "b"],
    "rgb_vector": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    "rgba_vector": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]],
    "vec2f_vector": [[1.0, 2.0], [3.0, 4.0]],
    "vec2d_vector": [[1.0, 2.0], [3.0, 4.0]],
    "vec3f_vector": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "vec3d_vector": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "vec4f_vector": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]],
    "vec4d_vector": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]],
    "mat4f_vector": [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
                      [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]],
                     [[17.0, 18.0, 19.0, 20.0], [21.0, 22.0, 23.0, 24.0],
                      [25.0, 26.0, 27.0, 28.0], [29.0, 30.0, 31.0, 32.0]]],
    "mat4d_vector": [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0],
                      [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]],
                     [[17.0, 18.0, 19.0, 20.0], [21.0, 22.0, 23.0, 24.0],
                      [25.0, 26.0, 27.0, 28.0], [29.0, 30.0, 31.0, 32.0]]],
    "scene_object_vector": [],
}


def make_context(proxy_mode=False):
    """Returns a new SceneContext searching the test DSO directory."""
    context = scene_rdl2.SceneContext()
    context.setDsoPath(TEST_DSO_PATH)
    context.setProxyModeEnabled(proxy_mode)
    return context


def write_scene(context, path, delta_encoding=False, transient_encoding=False):
    """Writes the context with AsciiWriter (.rdla) or BinaryWriter (.rdlb)."""
    if path.endswith(".rdla"):
        writer = scene_rdl2.AsciiWriter(context)
    else:
        writer = scene_rdl2.BinaryWriter(context)
        writer.setTransientEncoding(transient_encoding)
    writer.setDeltaEncoding(delta_encoding)
    writer.toFile(path)


def read_scene(context, path):
    """Reads a .rdla or .rdlb file into the context."""
    if path.endswith(".rdla"):
        scene_rdl2.AsciiReader(context).fromFile(path)
    else:
        scene_rdl2.BinaryReader(context).fromFile(path)


def names(objects):
    """Returns the names of a list of SceneObjects, keeping None entries."""
    return [o.getName() if o is not None else None for o in objects]


def build_builtin_scene(context):
    """Fills a context with a small scene that needs no DSOs."""
    scene_vars = context.getSceneVariables()
    scene_vars.set("image_width", 640)
    scene_vars.set("image_height", 360)
    user_data = context.createSceneObject("UserData", "data").toUserData()
    user_data.setFloatData("weights", [0.25, 0.75])


def check_builtin_scene(test, context):
    """Checks a context against build_builtin_scene()."""
    scene_vars = context.getSceneVariables()
    test.assertEqual(scene_vars.get("image_width"), 640)
    test.assertEqual(scene_vars.get("image_height"), 360)
    user_data = context.getSceneObject("data").toUserData()
    test.assertEqual(user_data.getFloatKey(), "weights")
    test.assertEqual(user_data.getFloatValues().toList(), [0.25, 0.75])


def set_metadata(metadata):
    metadata.set("name", ["blah", "foo"])
    metadata.set("type", ["int", "string"])
    metadata.set("value", ["2", "abcd"])


# Values TestAscii/TestBinary::testRoundtrip set on "/seq/shot/pizza".
# Blurrable attributes get a (TIMESTEP_BEGIN, TIMESTEP_END) pair.
PIZZA_BLURRED = {
    "int": (100, 101),
    "long": (102, 103),
    "float": (3.0, 4.0),
    "double": (5.0, 6.0),
    "rgb": ([0.2, 0.3, 0.4], [0.3, 0.4, 0.5]),
    "rgba": ([0.2, 0.3, 0.4, 0.5], [0.3, 0.4, 0.5, 0.6]),
    "vec2f": ([1.0, 2.0], [2.0, 3.0]),
    "vec2d": ([2.0, 3.0], [3.0, 4.0]),
    "vec3f": ([1.0, 2.0, 3.0], [2.0, 3.0, 4.0]),
    "vec3d": ([2.0, 3.0, 4.0], [3.0, 4.0, 5.0]),
    "vec4f": ([1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]),
    "vec4d": ([2.0, 3.0, 4.0, 5.0], [3.0, 4.0, 5.0, 6.0]),
    "mat4f": ([16.0, 15.0, 14.0, 13.0,
               12.0, 11.0, 10.0, 9.0,
               8.0, 7.0, 6.0, 5.0,
               4.0, 3.0, 2.0, 1.0],
              [32.0, 31.0, 30.0, 29.0,
               28.0, 27.0, 26.0, 25.0,
               24.0, 23.0, 22.0, 21.0,
               20.0, 19.0, 18.0, 17.0]),
    "mat4d": ([16.0, 15.0, 14.0, 13.0,
               12.0, 11.0, 10.0, 9.0,
               8.0, 7.0, 6.0, 5.0,
               4.0, 3.0, 2.0, 1.0],
              [32.0, 31.0, 30.0, 29.0,
               28.0, 27.0, 26.0, 25.0,
               24.0, 23.0, 22.0, 21.0,
               20.0, 19.0, 18.0, 17.0]),
}
PIZZA_VALUES = {
    "bool": False,
    "string": "not a pizza",
    "bool_vector": [False, True],
    "int_vector": [42, 43],
    "long_vector": [44, 45],
    "float_vector": [4.0, 5.0],
    "double_vector": [4.0, 5.0],
    "string_vector": ["c", "d"],
    "rgb_vector": [[0.5, 0.6, 0.7], [0.8, 0.9, 0.1]],
    "rgba_vector": [[0.5, 0.6, 0.7, 0.8], [0.9, 0.1, 0.2, 0.3]],
    "vec2f_vector": [[4.0, 5.0], [6.0, 7.0]],
    "vec2d_vector": [[4.0, 5.0], [6.0, 7.0]],
    "vec3f_vector": [[4.0, 5.0, 6.0], [6.0, 7.0, 8.0]],
    "vec3d_vector": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "vec4f_vector": [[4.0, 5.0, 6.0, 7.0], [7.0, 8.0, 9.0, 10.0]],
    "vec4d_vector": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]],
    "mat4f_vector": [[16.0, 15.0, 14.0, 13.0,
                      12.0, 11.0, 10.0, 9.0,
                      8.0, 7.0, 6.0, 5.0,
                      4.0, 3.0, 2.0, 1.0],
                     [32.0, 31.0, 30.0, 29.0,
                      28.0, 27.0, 26.0, 25.0,
                      24.0, 23.0, 22.0, 21.0,
                      20.0, 19.0, 18.0, 17.0]],
    "mat4d_vector": [[16.0, 15.0, 14.0, 13.0,
                      12.0, 11.0, 10.0, 9.0,
                      8.0, 7.0, 6.0, 5.0,
                      4.0, 3.0, 2.0, 1.0],
                     [32.0, 31.0, 30.0, 29.0,
                      28.0, 27.0, 26.0, 25.0,
                      24.0, 23.0, 22.0, 21.0,
                      20.0, 19.0, 18.0, 17.0]],
}


def build_roundtrip_scene():
    """Returns the context that TestAscii/TestBinary::testRoundtrip build."""
    context = make_context()
    pizza = context.createSceneObject("ExtensiveObject", "/seq/shot/pizza")
    cookie = context.createSceneObject("ExtensiveObject", "/seq/shot/cookie")
    teapot = context.createSceneObject("FakeTeapot", "/seq/shot/teapot")
    light = context.createSceneObject("FakeLight", "/seq/shot/light")
    material = context.createSceneObject("FakeMaterial", "/seq/shot/material")

    for name, (begin, end) in PIZZA_BLURRED.items():
        pizza.set(name, begin, 0)
        pizza.set(name, end, 1)
    for name, value in PIZZA_VALUES.items():
        pizza.set(name, value)
    pizza.setBinding("string", cookie)
    pizza.set("scene_object", teapot)
    pizza.set("scene_object_vector", [light, material])

    # Set the Metadata attributes directly, as the C++ test does;
    # Metadata.setAttributes bypasses change tracking (see test_metadata.py).
    set_metadata(context.createSceneObject("Metadata", "/seq/shot/metadata"))
    return context


def check_roundtrip_scene(test, original, result):
    """Checks a context that was read back against the original
    build_roundtrip_scene() context."""
    pizza = original.getSceneObject("/seq/shot/pizza")
    read_pizza = result.getSceneObject("/seq/shot/pizza")
    for name in PIZZA_BLURRED:
        for timestep in (0, 1):
            test.assertValuesEqual(read_pizza.get(name, timestep),
                                   pizza.get(name, timestep),
                                   msg="%s[%d]" % (name, timestep))
    for name in PIZZA_VALUES:
        test.assertValuesEqual(read_pizza.get(name), pizza.get(name), msg=name)

    test.assertEqual(read_pizza.getBinding("string").getName(), "/seq/shot/cookie")
    read_teapot = read_pizza.get("scene_object")
    test.assertEqual(read_teapot.getName(), "/seq/shot/teapot")
    test.assertEqual(read_teapot.getSceneClass().getName(), "FakeTeapot")
    things = read_pizza.get("scene_object_vector").toList()
    test.assertEqual([(t.getName(), t.getSceneClass().getName()) for t in things],
                     [("/seq/shot/light", "FakeLight"),
                      ("/seq/shot/material", "FakeMaterial")])

    # The untouched cookie should read back with every default intact.
    cookie = original.getSceneObject("/seq/shot/cookie")
    read_cookie = result.getSceneObject("/seq/shot/cookie")
    for name in cookie.getAttributeNames():
        for timestep in (0, 1) if name in PIZZA_BLURRED else (0,):
            test.assertValuesEqual(read_cookie.get(name, timestep),
                                   cookie.get(name, timestep),
                                   msg="%s[%d]" % (name, timestep))
    test.assertIsNone(read_cookie.getBinding("string"))

    read_metadata = result.getSceneObject("/seq/shot/metadata").toMetadata()
    test.assertEqual(read_metadata.getAttributeNames().toList(), ["blah", "foo"])
    test.assertEqual(read_metadata.getAttributeTypes().toList(), ["int", "string"])
    test.assertEqual(read_metadata.getAttributeValues().toList(), ["2", "abcd"])


def check_roundtrip(test, filename, transient_encoding=False):
    """Writes build_roundtrip_scene() to a file named filename, whose extension
    picks the format, reads it into a new context, and checks the result."""
    original = build_roundtrip_scene()
    path = test.temp_path(filename)
    write_scene(original, path, transient_encoding=transient_encoding)
    result = make_context()
    read_scene(result, path)
    check_roundtrip_scene(test, original, result)


def check_delta_encoding(test, ext):
    """The body of TestAscii/TestBinary::testDeltaEncoding, for the format with
    the file extension ext."""
    context = make_context()
    teapot = context.createSceneObject("FakeTeapot", "/seq/shot/teapot")
    metadata = context.createSceneObject("Metadata", "/seq/shot/metadata")

    # Everything is new, so a delta holds everything.
    path = test.temp_path("delta1" + ext)
    write_scene(context, path, delta_encoding=True)
    result = make_context()
    read_scene(result, path)
    test.assertTrue(result.sceneObjectExists("/seq/shot/teapot"))
    test.assertTrue(result.sceneObjectExists("/seq/shot/metadata"))

    # After committing, nothing has changed, so a delta is empty.
    context.commitAllChanges()
    path = test.temp_path("delta2" + ext)
    write_scene(context, path, delta_encoding=True)
    result = make_context()
    read_scene(result, path)
    test.assertFalse(result.sceneObjectExists("/seq/shot/teapot"))
    with test.assertRaises(ValueError):
        result.getSceneObject("/seq/shot/teapot")

    # Changed objects come back.
    teapot.set("fakeness", 99.99)
    set_metadata(metadata)
    path = test.temp_path("delta3" + ext)
    write_scene(context, path, delta_encoding=True)
    result = make_context()
    read_scene(result, path)
    test.assertAlmostEqual(result.getSceneObject("/seq/shot/teapot").get("fakeness"),
                           99.99, places=4)
    read_metadata = result.getSceneObject("/seq/shot/metadata").toMetadata()
    test.assertEqual(read_metadata.getAttributeValues().toList(), ["2", "abcd"])


def check_null_references(test, ext):
    """The body of TestAscii/TestBinary::testNullReferences, for the format
    with the file extension ext: reading a file back into the same context
    restores null references."""
    context = make_context()
    objs = {n: context.createSceneObject("ExtensiveObject", "/seq/shot/" + n)
            for n in ["pizza", "cookie", "mango", "apple", "sharknado", "explosion"]}
    pizza = objs["pizza"]
    pizza.set("scene_object", None)
    pizza.set("scene_object_vector", [objs["mango"], None, objs["sharknado"]])
    pizza.set("string", "not a pizza")
    pizza.setBinding("string", None)
    test.assertIsNone(pizza.get("scene_object"))
    test.assertIsNone(pizza.get("scene_object_vector").toList()[1])
    test.assertIsNone(pizza.getBinding("string"))

    path = test.temp_path("nullrefs" + ext)
    write_scene(context, path)

    pizza.set("scene_object", objs["cookie"])
    pizza.set("scene_object_vector", [objs["mango"], objs["apple"], objs["sharknado"]])
    pizza.setBinding("string", objs["explosion"])
    test.assertIsNotNone(pizza.get("scene_object_vector").toList()[1])

    read_scene(context, path)
    test.assertIsNone(pizza.get("scene_object"))
    test.assertIsNone(pizza.get("scene_object_vector").toList()[1])
    test.assertIsNone(pizza.getBinding("string"))
    test.assertEqual(pizza.get("string"), "not a pizza")


def to_python(value):
    """Recursively converts binding values (Vec3f, Mat4f, IntVector, ...) into
    plain lists, so tests can compare them against literals."""
    if hasattr(value, "toList"):
        value = value.toList()
    if isinstance(value, (list, tuple)):
        return [to_python(v) for v in value]
    return value


class Rdl2TestCase(unittest.TestCase):
    """TestCase with comparisons for the float-based binding types."""

    def temp_path(self, filename):
        """Returns a path in a temporary directory removed after the test."""
        if not hasattr(self, "_tmpdir"):
            self._tmpdir = tempfile.TemporaryDirectory()
            self.addCleanup(self._tmpdir.cleanup)
        return os.path.join(self._tmpdir.name, filename)

    def assertValuesEqual(self, actual, expected, msg=None):
        """Compares nested values exactly, after converting binding objects
        with toList() to plain lists."""
        self.assertEqual(to_python(actual), to_python(expected), msg)

    def assertValuesAlmostEqual(self, actual, expected, places=5, msg=None):
        """Compares nested numeric sequences (or binding objects with
        toList()) element by element. Non-numeric leaves compare exactly."""
        actual = to_python(actual)
        expected = to_python(expected)
        if isinstance(expected, list):
            self.assertIsInstance(actual, list, msg)
            self.assertEqual(len(actual), len(expected), msg)
            for a, e in zip(actual, expected):
                self.assertValuesAlmostEqual(a, e, places, msg)
        elif isinstance(expected, float):
            self.assertAlmostEqual(actual, expected, places=places, msg=msg)
        else:
            self.assertEqual(actual, expected, msg)
