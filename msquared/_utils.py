"""
Utility functions.
"""
from typing import List
import os
import re
import glob

def _handle_str(string_param: str) -> List[str]:
    if isinstance(string_param, str):
        return [string_param]
    return string_param

# Returns a set all files in the provided paths.
def _locate_files(paths: List[str]) -> List[str]:
    files: List[str] = []
    for path in paths:
        # Make sure to eliminate all folders
        files += [os.path.relpath(filename) for filename in glob.iglob(path + "/**", recursive=True) if os.path.isfile(filename)]
    return files

# Finds all #include's in a file.
def _find_included_files(filename: str):
    included_files: List[str] = []
    with open(filename, 'r') as file:
        # Match includes of the form #include <.*> and #include ".*"
        included_files.extend(re.findall('#include [<"]([^>"]*)[>"]', file.read()))
    return included_files
