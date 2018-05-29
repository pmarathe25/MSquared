#!/usr/bin/python3
import msquared as m2

# Add this directory to the project.
make_gen = m2.MGen("./")
# # Make sure we compile/link with optimizations enabled and C++17.
make_gen.flags += "-O3 -flto -march=native"
make_gen.cflags += "-std=c++17"
# Add library
make_gen.add_target("lib/libtest.so", deps=["src/*.cpp"], alias="lib")
# Also include a target to execute. Explicitly specify header, since it's outside project dirs.
make_gen.add_target("test/test", deps=["lib/libtest.so", "test/test.cpp", "/usr/local/include/MsquaredTest"], execute="test")
# # Add a target to install headers.
make_gen.add_target("/usr/local/include/MsquaredTest", deps="include/*.hpp", alias="install", clean=False)
# DEBUG:
print(make_gen.generate())
# Write the makefile
make_gen.write("makefile")
