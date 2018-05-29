#!/usr/bin/python3
import msquared as m2

# Add this directory to the project.
mgen = m2.MGen("./")
# # Make sure we compile/link with optimizations enabled and C++17.
mgen.flags += "-O3 -flto -march=native"
mgen.cflags += "-std=c++17"
# Add library
mgen.add_target("lib/libtest.so", deps=["src/*.cpp"], alias="lib")
# Also include a target to execute. Explicitly specify header, since it's outside project dirs.
mgen.add_target("test/test", deps=["lib/libtest.so", "test/test.cpp", "/usr/local/include/MsquaredTest"], execute="test")
# # Add a target to install headers.
# mgen.add_target("/usr/local/include/MsquaredTest", deps="include/*.hpp", alias="install", clean=False)
m2.add_installation(mgen, "include/**.hpp", "/usr/local/include/MsquaredTest")
# DEBUG:
print(mgen.generate())
# Write the makefile
mgen.write("makefile")
