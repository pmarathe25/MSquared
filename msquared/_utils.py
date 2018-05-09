"""
Utility functions.
"""
from typing import List
import os
import glob

def _handle_str(string_param: str) -> List[str]:
    if isinstance(string_param, str):
        return [string_param]
    return string_param

# Returns a set all files in the provided paths.
def _locate_files(paths: List[str]) -> List[str]:
    files = []
    for path in paths:
        # Make sure to eliminate all folders
        files += [filename for filename in glob.iglob(path + "/**", recursive=True) if os.path.isfile(filename)]
    return files
