#!/usr/bin/python3
import msquared as m2
import unittest
import subprocess
import shutil
import os

class MSquaredTest(unittest.TestCase):
    def setUp(self):
        self.mgen = m2.MGen("./", project_include_dirs="./include")
        self.makefile_path = os.path.join(self.mgen.root_dir, "Makefile")
        sources = m2.wrap("src/", ["factorial", "fibonacci"], ".cpp")
        self.libname = "libtest.so"
        self.install_directory = os.path.join(self.mgen.root_dir, "install")
        self.mgen.add_library(self.libname, sources=sources, libraries="pthread", install_directory=self.install_directory)

    def test_negative_source_missing_library(self):
        sources = m2.wrap("src/", ["fake"], ".cpp")
        self.assertRaises(FileNotFoundError, self.mgen.add_library, "test", sources=sources)

    def test_negative_source_missing_executable(self):
        sources = m2.wrap("src/", ["fake"], ".cpp")
        self.assertRaises(FileNotFoundError, self.mgen.add_executable, "test", sources=sources)

    def test_negative_build_dir_invalid(self):
        self.assertRaises(OSError, self.mgen.set_build_dir, build_dir="/")

    def test_library_install_uninstall(self):
        self.mgen.write(self.makefile_path)
        status = subprocess.call(["make", "-j8", "-f", self.makefile_path, f"install_{self.libname}"])
        self.assertTrue(status == 0)
        self.assertTrue(os.path.exists(os.path.join(self.install_directory, self.libname)))
        status = subprocess.call(["make", "-j8", "-f", self.makefile_path, f"uninstall_{self.libname}"])
        self.assertTrue(status == 0)
        self.assertFalse(os.path.exists(os.path.join(self.install_directory, self.libname)))

    def test_executable_builds(self):
        self.mgen.add_executable("test", sources="test/test.cpp", libraries=["libtest.so", "pthread"])
        self.mgen.write(self.makefile_path)
        status = subprocess.call(["make", "-j8", "-f", self.makefile_path])
        self.assertTrue(status == 0)

    def test_file_install_uninstall(self):
        filename = "utils.hpp"
        filepath = os.path.join(self.mgen.root_dir, "include", filename)
        self.mgen.add_install(path=filepath, install_directory=self.install_directory)
        self.mgen.write(self.makefile_path)
        status = subprocess.call(["make", "-j8", "-f", self.makefile_path, f"install_{filename}"])
        self.assertTrue(status == 0)
        self.assertTrue(os.path.exists(os.path.join(self.install_directory, filename)))
        status = subprocess.call(["make", "-j8", "-f", self.makefile_path, f"uninstall_{filename}"])
        self.assertTrue(status == 0)
        self.assertFalse(os.path.exists(os.path.join(self.install_directory, filename)))

    def tearDown(self):
        pass
        # if os.path.exists(self.mgen.build_dir):
        #     shutil.rmtree(f"{self.mgen.build_dir}")
        # if os.path.exists(self.install_directory):
        #     shutil.rmtree(f"{self.install_directory}")
        # if os.path.exists(self.makefile_path):
        #     os.remove(self.makefile_path)

if __name__ == '__main__':
    unittest.main()
