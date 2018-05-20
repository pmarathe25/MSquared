#!/usr/bin/python3
import unittest
import msquared as m2

class MSquaredTest(unittest.TestCase):
    def setUp(self):
        # Add this directory to the project.
        self.make_gen = m2.MGen("./")

    def test_generate_project_makefile(self):
        # Make sure we compile/link with optimizations enabled.
        self.make_gen.add_flags("-O3 -flto -march=native")
        # Also compile with c++-17.
        self.make_gen.add_cflags("-std=c++17")
        # Create a new target with the path to desired executable and use the source file(s) involved.
        # Should be removed during clean!
        self.make_gen.add_library("lib/libtest.so", ["src/source1.cpp", "src/source2.cpp"], clean=True)
        self.make_gen.add_executable("test/test", "test/test.cpp", clean=True, libraries=["lib/libtest.so", "pthread"])
        # Add a custom target that will run the test executable.
        self.make_gen.add_custom_target("test", commands="test/test", dependencies="test/test")
        self.make_gen.add_custom_target("lib", phony=True, dependencies="lib/libtest.so")
        # Add a target to install headers.
        m2.add_installation(self.make_gen, headers="include/*.hpp", install_file="/usr/local/include/MSquaredTest/msquared.hpp")
        # Write the makefile
        self.make_gen.write("makefile")
        # DEBUG:
        print(self.make_gen.generate())

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
