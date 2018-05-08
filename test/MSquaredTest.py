#!/usr/bin/python3
import unittest
import msquared as m2

class MSquaredTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_generate_project_makefile(self):
        make_gen = m2.MGen()
        # Make sure we compile/link with optimizations enabled.
        make_gen.add_flags("-O3 -flto -march=native")
        # Also compile with c++-17.
        make_gen.add_cflags("-std=c++17")
        # Create a new target with the path to desired executable and use the source file(s) involved.
        make_gen.add_executable("test/test", "test/test.cpp")
        # Create a clean target passing in extra files to be deleted
        # (by default, only the build directory is emptied)
        make_gen.add_clean("test/test")
        # Generate the makefile
        make_gen.generate("./makefile")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
