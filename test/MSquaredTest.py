#!/usr/bin/python3
import msquared as m2

# Add this directory to the project.
make_gen = m2.MGen("./")
# Make sure we compile/link with optimizations enabled.
make_gen.add_flags("-O3 -flto -march=native")
# Also compile with c++-17.
make_gen.add_cflags("-std=c++17")
# Create a new target with the path to desired executable and use the source file(s) involved.
# Should be removed during clean!
make_gen.register_library("lib/libtest.so", "src/*.cpp", clean=True)
make_gen.register_executable("test/test", source_files="test/test.cpp", clean=True, libraries="lib/libtest.so")
# Add a custom target that will run the test executable.
make_gen.register_custom_target("test", commands="test/test", dependencies="test/test")
make_gen.register_custom_target("lib", phony=True, dependencies="lib/libtest.so")
# Add a target to install headers.
m2.add_installation(make_gen, headers="include/*.hpp", install_file="/usr/local/include/MSquaredTest/msquared.hpp")
# Write the makefile
make_gen.write("makefile")
