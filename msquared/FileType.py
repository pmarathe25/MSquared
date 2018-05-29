from enum import IntEnum
import os

class FileType(IntEnum):
    SOURCE = 0
    OBJECT = 1
    SHARED_OBJECT = 2
    EXECUTABLE = 3
    HEADER = 4

def file_type(filename: str) -> FileType:
    if os.path.splitext(filename)[1] == ".so":
        return FileType.SHARED_OBJECT
    elif os.path.splitext(filename)[1] == ".o":
        return FileType.OBJECT
    elif '.c' in os.path.splitext(filename)[1]:
        # Match most C/C++ source extensions.
        return FileType.SOURCE
    elif '.h' in os.path.splitext(filename)[1]:
        # Match most C/C++ header extensions.
        return FileType.HEADER
    return FileType.EXECUTABLE
