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
        self.make_gen.add_executable("test/test", "test/test.cpp")
        # Create a clean target passing in extra files to be deleted
        # (by default, only the build directory is emptied)
        self.make_gen.add_clean("test/test")
        # Generate the makefile
        self.make_gen.generate("./makefile")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
