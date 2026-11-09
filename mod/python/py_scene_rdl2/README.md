Python Bindings for scene_rdl2
==============================

py_scene_rdl2 delivers Python bindings for scene_rdl2 using boost::python.
These were originally delivered with the usd_rdl2 package but delivering them
with scene_rdl2 makes more sense, so they were moved here.

Usage
=====

Python bindings are delivered in the **scene_rdl2** python package.

API usage generally follows the scene_rdl2 C++ APIs.

Start with a rez2 environment that includes moonshine or moonbase_proxies:

```bash
rez2
rez-env scene_rdl2 moonshine
python
```

Then set up a SceneContext and get to work:

```python
import scene_rdl2

context = scene_rdl2.SceneContext()
context.setProxyModeEnabled(True)  # set this to use proxy mode
context.loadAllSceneClasses()

camera = context.createSceneObject("PerspectiveCamera", "shot_cam")
camera.set("focal", 24.98)
camera.set("mb_shutter_open", -0.6)
camera.set("mb_shutter_close", 0)

scenevars = context.getSceneVariables()
scenevars.set("camera", camera)

scene_rdl2.writeSceneToFile(context, "example.rdla")
```

This code creates and outputs example.rdla:

```lua
SceneVariables {
    ["camera"] = PerspectiveCamera("shot_cam"),
}

PerspectiveCamera("shot_cam") {
    ["mb_shutter_open"] = -0.600000024,
    ["mb_shutter_close"] = 0,
    ["focal"] = blur(24.9799995, 24.9799995),
}
```

Testing
=======

Tests for these bindings live in `tests/mod/python/py_scene_rdl2` and use
only the standard library's `unittest` module. CTest runs each file as its own
test, `scenerdl2_py_scene_rdl2_<file>` (for example
`scenerdl2_py_scene_rdl2_test_ascii`), labeled `unit`, with the Python
interpreter the bindings were built against and `-X faulthandler`, so a binding
that aborts or crashes the interpreter fails only its own file and prints a
Python traceback. From the build directory:

```bash
ctest -C Release -R py_scene_rdl2 --output-on-failure
```

To run them by hand, point `PYTHONPATH` at the module's build directory and
`SCENE_RDL2_TEST_DSO_PATH` at the directory holding the scene_rdl2 C++ unit
test DSOs (ExtensiveObject, FakeTeapot, ...), which tests needing SceneClasses
beyond the built-in ones use. Without `SCENE_RDL2_TEST_DSO_PATH`, those tests
are skipped.

```bash
PYTHONPATH=<build>/moonray/scene_rdl2/mod/python/py_scene_rdl2 \
SCENE_RDL2_TEST_DSO_PATH=<build>/moonray/scene_rdl2/tests/lib/scene/rdl2/<config> \
python3 -m unittest discover -s tests/mod/python/py_scene_rdl2 -v
```

New or changed bindings should come with tests here. Where a binding is known
to be broken or missing, its test is checked in commented out under a `TODO`
describing the fix; uncomment it as part of fixing the binding. The assertions
in these tests have not run, so check them against the binding when you do.

The Python tests follow the C++ tests in `tests/lib/scene/rdl2` file for file and
test for test: `TestAscii.cc` corresponds to `test_ascii.py`, and
`TestAscii::testRoundtrip` to `test_roundtrip` in it. Each such test says so in a
`# Mirrors TestClass::testName.` comment, followed by `# Omits:` for anything the
C++ test checks that the Python test does not. A test with no such comment has no
C++ counterpart, and neither does a file whose docstring says so, such as
`test_math_types.py` (C++ `TestTypes` covers string conversion instead).

The bindings register no exception translators, so Boost.Python's defaults
apply: where the C++ tests expect `except::KeyError`, the Python tests expect
`ValueError`, and where they expect `except::TypeError`, `RuntimeError`.

These C++ tests have no Python mirror, because they check internals or C++-only
features that the bindings do not expose:

- All of `TestTypes`, `TestValueContainer`, `TestDso`, `TestDsoFinder`,
  `TestCreateDirectories`, and `TestSplit`
- `TestAttribute`: `testConstructBlurrable`, `testConstructWithDefault`,
  `testIndex`, `testOffset`
- `TestAttributeKey`: `testIndex`, `testOffset`, `testFlags`, `testObjectType`
- `TestSceneClass`: `testDeclareSimple`, `testDeclareSimpleWithDefault`,
  `testDeclareBindable`, `testDeclareBindableWithDefault`,
  `testDeclareBlurrable`, `testDeclareBlurrableWithDefault`, `testMemoryLayout`,
  `testCreateDestroyObject`, `testAttributeStorage`
- `TestSceneObject`: `testExtension`

Two C++ tests are disabled in the C++ suite and have no Python mirror:
`TestAscii::testMemory` (a leak check behind a compile-time flag) and
`TestSceneObject::testInterpolatedGet`. A third, `TestAscii::testDenormals`, is
also disabled in C++ but is mirrored, on a subset of its values.
