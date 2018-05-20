from enum import IntEnum
from typing import List, Set

class TargetType(IntEnum):
    INTERMEDIATE = 0
    LIBRARY = 1
    EXECUTABLE = 2

class Target(object):
    def __init__(self, type: TargetType, sources: List[str], obj_files: Set[str] = set(), pre_flags: str = "", post_flags: str = ""):
        self.type: TargetType = type
        self.sources: List[str] = sources
        self.pre_flags: str = pre_flags
        self.post_flags: str = post_flags
        self.obj_files: Set[str] = obj_files
