# Copyright 2026 DreamWorks Animation LLC
# SPDX-License-Identifier: Apache-2.0

# Tests for the scene_rdl2 Python bindings, written with the standard library's
# unittest module so they need nothing beyond the Python the bindings were
# built against.

set(module __${PACKAGE_NAME}__)

if(NOT TARGET ${module} OR NOT Python_Interpreter_FOUND)
    message(WARNING "Skipping the scene_rdl2 Python binding tests: "
                    "they need the ${module} target and a Python interpreter.")
    return()
endif()

# One CTest test per file, so a binding that aborts or crashes the interpreter
# fails only its own file. -X faulthandler prints the Python traceback when
# that happens.
#
# PYTHONPATH points at the module's build directory, which also holds the
# __init__.py and "scene_rdl2" symlink that make "import scene_rdl2" work
# before install. The test DSOs (ExtensiveObject, etc.) are the ones built for
# the C++ scene_rdl2 unit tests.
file(GLOB test_files CONFIGURE_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/test_*.py)
foreach(test_file ${test_files})
    get_filename_component(test_name ${test_file} NAME_WE)
    set(target scenerdl2_py_scene_rdl2_${test_name})
    add_test(NAME ${target}
        COMMAND ${Python_EXECUTABLE} -X faulthandler -m unittest discover
                -s ${CMAKE_CURRENT_SOURCE_DIR}
                -p ${test_name}.py
                -v
    )
    set_tests_properties(${target} PROPERTIES
        LABELS "unit"
        ENVIRONMENT "PYTHONPATH=$<TARGET_FILE_DIR:${module}>;SCENE_RDL2_TEST_DSO_PATH=$<TARGET_FILE_DIR:scenerdl2_scene_rdl2_tests>;PYTHONDONTWRITEBYTECODE=1"
    )
endforeach()
