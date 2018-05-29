"""
Utility functions.
"""
from typing import List
from enum import IntEnum
import glob
import os
import re

class FileType(IntEnum):
    SOURCE = 0
    OBJECT = 1
    SHARED_OBJECT = 2
    EXECUTABLE = 3

def _file_type(filename: str) -> FileType:
    if os.path.splitext(filename)[1] == ".so":
        return FileType.SHARED_OBJECT
    elif os.path.splitext(filename)[1] == ".o":
        return FileType.OBJECT
    elif '.c' in os.path.splitext(filename)[1]:
        return FileType.SOURCE
    return FileType.EXECUTABLE

# Prepends a string with a prefix only if the string does not already have that prefix.
def _prefix(prefix: str, input_string: str) -> str:
    if input_string.starwith(prefix):
        return input_string
    return prefix + input_string

def _suffix(input_string: str, suffix: str) -> str:
    if input_string.endswith(suffix):
        return input_string
    return input_string + suffix

def _ends_with(input_string: str, ending: str) -> bool:
    return input_string.strip().endswith(ending)

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


# Returns a set all files in the provided paths.
# def _locate_files_in_paths(paths: List[str]) -> List[str]:
#     files: List[str] = []
#     for path in paths:
#         # Make sure to eliminate all folders
#         files += [os.path.relpath(filename) for filename in glob.iglob(path + "/**", recursive=True) if os.path.isfile(filename)]
#     return files
#
# # Given the name/path of a file, find potential matches in files.
# def _find_file_in_list(filename: str, files: List[str]) -> List[str]:
#     filename = os.path.relpath(filename)
#     possible_matches: List[str] = []
#     for search_filename in files:
#         # FIXME: Needs to search properly. filename = core/Tensor3.hpp <-- Look in project dirs.
#         if filename == search_filename or filename == search_filename.split('/')[-1]:
#             print("Searching for: " + str(filename) + " in: " + str(search_filename))
#             # Either the path matches exactly, or the file name patches exactly.
#             possible_matches.append(search_filename)
#     return possible_matches
#
# # If there are multiple matching files, the user needs to specify which one to use.
# def _prompt_user_disambiguate_dependency(dependency: str, matching_project_files: List[str], source_file: str) -> str:
#     # Make sure that the selected file actually corresponds to one of the choices.
#     matched_file = input("For dependency '" + dependency + "' of '" + source_file + "', found multiple candidates: "
#         + str(matching_project_files) + ". Please choose one.\n>>> ")
#     potential_matches = _find_file_in_list(matched_file, matching_project_files)
#     while len(potential_matches) != 1:
#         matched_file = input("ERROR: '" + matched_file + "' did not match one of "
#             + str(matching_project_files) + ". Try providing the full path.\n>>> ")
#         potential_matches = _find_file_in_list(matched_file, matching_project_files)
#     return potential_matches[0]
#
# def _expand_glob_list(glob_list: List[str]):
#     glob_list = _convert_to_list(glob_list)
#     # Expand any globs within the headers. Also get absolute paths.
#     expanded_glob_set: Set[str] = set()
#     for glob_expr in glob_list:
#         expanded_glob = [os.path.abspath(item) for item in glob.glob(glob_expr, recursive=True)]
#         expanded_glob_set.update(expanded_glob if expanded_glob else [glob_expr])
#     return expanded_glob_set
