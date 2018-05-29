#!/usr/bin/python3
import msquared as m2

# Add this directory to the project.
make_gen = m2.MGen("./")
# # Make sure we compile/link with optimizations enabled and C++17.
make_gen.flags += "-O3 -flto -march=native"
make_gen.cflags += "-std=c++17"
# # Create a new target with the path to desired executable and use the source file(s) involved.
# # Should be removed during clean!
# make_gen.register_library("lib/libtest.so", "src/*.cpp", clean=True) \
#     .register_executable("test/test", source_files="test/test.cpp", clean=True, libraries="lib/libtest.so")
# # Add a custom target that will run the test executable.
# make_gen.register_custom_target("test", commands="test/test", dependencies="test/test") \
#     .register_custom_target("lib", phony=True, dependencies="lib/libtest.so")
# # Add a target to install headers.
# m2.add_installation(make_gen, headers="include/*.hpp", install_file="/usr/local/include/MSquaredTest/msquared.hpp")
# # Write the makefile
# make_gen.write("makefile")
make_gen.add_target("lib/libtest.so", deps=["src/*.cpp"])
make_gen.add_target("test/test", deps=["lib/libtest.so", "test/test.cpp"])
# DEBUG:
print(make_gen.generate())
