"""
Utility functions.
"""
from typing import List
import glob
import re
import os

# Prepends a string with a prefix only if the string does not already have that prefix.
def _prefix(prefix: str, input_string: str) -> str:
    if input_string.starwith(prefix):
        return input_string
    return prefix + input_string

def _suffix(input_string: str, suffix: str) -> str:
    if input_string.endswith(suffix):
        return input_string
    return input_string + suffix

def _convert_to_iterable(obj) -> List:
    def is_iterable(obj):
        return not isinstance(obj, str) and (hasattr(obj, "__getitem__") or hasattr(obj, "__iter__"))
    if not is_iterable(obj):
        return [obj]
    return obj

def _wrapper_join(iterable, prefix: str = " ", suffix: str = "") -> str:
    joined: str = ""
    for elem in iterable:
        joined += prefix + elem + suffix
    return joined

# Finds all #include's in a file.
def _find_included_files(filename: str):
    included_files: List[str] = []
    with open(filename, 'r') as file:
        try:
            # Match includes of the form #include <.*> and #include ".*"
            included_files.extend(re.findall('(?:(?<!\/\/\s))#include [<"]([^>"]*)[>"]', file.read()))
        except UnicodeDecodeError:
            pass
    return included_files

def _expand_glob_list(glob_list: List[str]):
    # No need for duplicates
    expanded_glob_set: Set[str] = set()
    for glob_expr in glob_list:
        expanded_glob = glob.glob(glob_expr, recursive=True)
        expanded_glob_set.update(expanded_glob if expanded_glob else [glob_expr])
    return expanded_glob_set

def _disambiguate_files(items: List[str]):
    if not items:
        return None
    elif len(items) == 1:
        return items[0]
    else:
        # TODO: Prompt user here
        print(f"WARNING: Found multiple candidates: {items}. Automatically choosing first candidate.")
        return items[0]
