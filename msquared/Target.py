from typing import List, Set
from msquared import utils

# A Target represents a linked target, like a library or executable.
# It has cflags and include_dirs, which are propagated to constituent objects
# (based on deps), as well as lflags and link_dirs which it uses.
class Target(object):
    def __init__(self, name: str, sources=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), compiler=""):
        """
        Represents an executable or library.

        Args:
            name (str): The name of the executable or library.
            sources (Set[str]): The constituent .cpp files.
            libraries (Set[str]): Libraries that should be linked against this target.
            cflags (Set[str]): Compiler flags for this target.
            include_dirs (Set[str]): Include directories for this target.
            lflags (Set[str]): Linker flags for this target.
            link_dirs (Set[str]): Link directories for this target.
        """
        self.name = name
        self.sources = utils.convert_to_set(sources)
        self.libraries = utils.convert_to_set(libraries)
        self.cflags = utils.convert_to_set(cflags)
        self.include_dirs = utils.convert_to_set(include_dirs)
        self.lflags = utils.convert_to_set(lflags)
        self.link_dirs = utils.convert_to_set(link_dirs)
        self.compiler = compiler

# Represents a target in a makefile. This consists of a name, dependencies, and commands.
# TODO: Also add options for PHONY here?
class MakefileTarget(object):
    def __init__(self, name: str, dependencies = set(), commands = list()):
        self.name = name
        self.dependencies = utils.convert_to_set(dependencies)
        self.commands = utils.convert_to_list(commands)

    def __str__(self):
        cmd_sep = "\n\t"
        return f"{self.name}:{utils.prefix_join(self.dependencies)}{utils.prefix_join(self.commands, cmd_sep)}"

    def __repr__(self):
        return self.__str__()

    # Equality is based solely on the target name, since we cannot have duplicate names in the Makefile.
    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
