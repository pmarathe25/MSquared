#!/usr/bin/python3
import msquared as m2

# Add this directory to the project.
mgen = m2.MGen("./")
# Add library.
sources = m2.wrap("src/", ["factorial", "fibonacci"], ".cpp")
mgen.add_library("test", sources=sources)
# Also include a target to execute.
mgen.add_executable("test", sources="test/test.cpp", libraries="test")

# Add a target to install headers.
# mgen.add_target("/usr/local/include/MsquaredTest", deps="include/*.hpp", alias="install", clean=False)
# m2.add_installation(mgen, "include/**.hpp", "/usr/local/include/MsquaredTest")
# DEBUG:
print(mgen.generate())
# Write the makefile
mgen.write("makefile")
