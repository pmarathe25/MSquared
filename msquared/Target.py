from msquared._utils import _convert_to_list, _expand_glob_list
from enum import IntEnum
from typing import List, Set

class TargetType(IntEnum):
    INTERMEDIATE = 0
    LIBRARY = 1
    EXECUTABLE = 2

class Target(object):
    def __init__(self, type: TargetType, sources, obj_files=set(), shared_obj_files=set(), pre_flags: str = "", post_flags: str = ""):
        self.type: TargetType = type
        # Any globs in the dependent source files should be expanded.
        self.sources: List[str] = _expand_glob_list(sources)
        self.pre_flags: str = pre_flags
        self.post_flags: str = post_flags
        self.obj_files: Set[str] = obj_files
        self.shared_obj_files: Set[str] = shared_obj_files

    def __str__(self):
        return "Type: " + str(self.type) + "\tSources: " + str(self.sources) + "\tObject Files: " + str(self.obj_files) + "\tPreFlags: " + str(self.pre_flags) + "\tPostFlags: " + str(self.post_flags)
