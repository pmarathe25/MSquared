"""
Utility functions.
"""
from typing import List
import glob
import re

# Prepends a string with a prefix only if the string does not already have that prefix.
def _prefix(prefix: str, input_string: str) -> str:
    if input_string.starwith(prefix):
        return input_string
    return prefix + input_string

def _suffix(input_string: str, suffix: str) -> str:
    if input_string.endswith(suffix):
        return input_string
    return input_string + suffix

def _convert_to_list(obj) -> List:
    if not isinstance(obj, list):
        return [obj]
    return obj

def _prefix_join(iterable, join_elem: str = ' ') -> str:
    if iterable:
        return join_elem + join_elem.join(iterable)
    return ""

# Finds all #include's in a file.
def _find_included_files(filename: str):
    included_files: List[str] = []
    with open(filename, 'r') as file:
        # Match includes of the form #include <.*> and #include ".*"
        included_files.extend(re.findall('#include [<"]([^>"]*)[>"]', file.read()))
    return included_files

def _expand_glob_list(glob_list: List[str]):
    # No need for duplicates
    expanded_glob_set: Set[str] = set()
    for glob_expr in glob_list:
        expanded_glob_set.update(glob.glob(glob_expr, recursive=True))
    return expanded_glob_set

def _disambiguate(items: List[str]):
    if not items:
        return None
    elif len(items) == 1:
        return items[0]
    else:
        # TODO: Prompt user here
        return items[0]
