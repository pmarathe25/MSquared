from typing import List, Set
from msquared import utils

# A Target represents a linked target, like a library or executable.
# It has cflags and include_dirs, which are propagated to constituent objects
# (based on deps), as well as lflags and link_dirs which it uses.
class Target(object):
    def __init__(self, name: str, sources=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set()):
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
