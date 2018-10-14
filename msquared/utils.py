"""
Utility functions.
"""
from typing import Set
import glob
import re
import os

# Prepends a string with a prefix only if the string does not already have that prefix.
def prefix(prefix: str, input_string: str) -> str:
    if input_string.startswith(prefix):
        return input_string
    return prefix + input_string

def suffix(input_string: str, suffix: str) -> str:
    if input_string.endswith(suffix):
        return input_string
    return input_string + suffix

def is_nonstring_iterable(obj):
    return not isinstance(obj, str) and (hasattr(obj, "__getitem__") or hasattr(obj, "__iter__"))

def convert_to_set(obj) -> Set:
    if isinstance(obj, set):
        return obj
    elif is_nonstring_iterable(obj):
        return set(obj)
    else:
        return set([obj])

# Locates paths in dirs. Returns a set of absolute paths.
def locate_paths(self, paths: Set[str], dirs: Set[str]):
    def check_project_dirs(file: str):
        for dir in dirs:
            # Project directories are guaranteed to be absolute paths.
            project_file = os.path.join(dir, file)
            if os.path.exists(project_file):
                return project_file
        raise FileNotFoundError("Could not find: " + str(file) + " in directories: " + str(dirs))

    paths = convert_to_set(files)
    dirs = convert_to_set(dirs)
    abspaths = set()
    for file in files:
        if os.path.exists(file):
            abspaths.add(file)
        else:
            abspaths.add(check_project_dirs(file))
    return abspaths

# Finds all #include's in a file.
def find_included_files(filename: str):
    included_files: Set[str] = set()
    with open(filename, 'r') as file:
        # try:
        # Match includes of the form #include <.*> and #include ".*" excluding commented out lines.
        included_files |= re.findall('(?:(?<!\/\/\s))#include [<"]([^>"]*)[>"]', file.read())
        # except UnicodeDecodeError:
        #     pass
    return included_files
