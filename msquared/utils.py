"""
Utility functions.
"""
from typing import Set
import os

# Prepends a string with a prefix only if the string does not already have that prefix.
def prefix(pre: str, input_string: str) -> str:
    if input_string.startswith(pre):
        return input_string
    return pre + input_string

def suffix(input_string: str, post: str) -> str:
    if input_string.endswith(post):
        return input_string
    return input_string + post

def suffix_before_extension(input_string: str, post: str) -> str:
    split_name = list(os.path.splitext(input_string))
    if split_name[0].endswith(post):
        return input_string
    split_name.insert(1, post)
    return ''.join(split_name)

def wrap(pre: str, input_string: str, post: str) -> str:
    return suffix(prefix(pre, input_string), post)

def hasext(path: str) -> bool:
    return bool(os.path.splitext(path)[1])

# Check if a directory or file requires root permissions to access or create.
def requires_root(dirname: str) -> bool:
    while not os.path.exists(dirname):
        dirname = os.path.abspath(os.path.join(dirname, os.pardir))
    return not os.access(dirname, os.W_OK)

# Joins elements of an iterable with a prefix.
def prefix_join(iterable, prefix = ' ') -> str:
    if len(iterable) > 0:
        return prefix + prefix.join(str(elem) for elem in iterable)
    return ""

def is_nonstring_iterable(obj):
    return not isinstance(obj, str) and (hasattr(obj, "__getitem__") or hasattr(obj, "__iter__"))

def convert_to(obj, ContainerType):
    if isinstance(obj, ContainerType):
        return obj
    elif is_nonstring_iterable(obj):
        return ContainerType(obj)
    elif obj:
        return ContainerType([obj])
    else:
        return ContainerType()

def convert_to_set(obj):
    return convert_to(obj, set)

def convert_to_list(obj):
    return convert_to(obj, list)

# Locates paths in dirs. Returns a set of absolute paths.
def locate_paths(paths: Set[str], dirs: Set[str], logger, ErrorType: type = None) -> Set[str]:
    """
    Attemps to locate paths in the specified directories.

    Args:
        paths (Set[str]): The paths to search for.
        dirs (Set[str]): The directories to search in. These should be absolute paths.
        logger (Logger): The logger to use.
        ErrorType (type): If provided, throws this type of error when a file cannot be found.

    Returns:
        If ErrorType is set:
            Set[str]: A set of absolute paths corresponding to the files found.
        otherwise:
            Tuple[Set[str], Set[str]]: A tuple whose first element is a set of absolute paths for files that were found, and whose second element is a set of paths for files that could not be found.

    """
    # Try to find the file in the provided directories.
    def check_dirs(path: str):
        for dir in dirs:
            # Project directories are guaranteed to be absolute paths.
            abspath = os.path.abspath(os.path.join(dir, path))
            if os.path.exists(abspath):
                logger.debug(f"Found {path} in {dir}. Using absolute path: {abspath}")
                return abspath
        err_msg = f"Could not find {path} in directories: {dirs}."
        logger.error(err_msg, ErrorType)

    paths = convert_to_set(paths)
    dirs = convert_to_set(dirs)
    abspaths = set()
    notfound = set()
    for path in paths:
        if os.path.exists(path) and os.path.isabs(path):
            logger.debug(f"{path} is already absolute.")
            abspaths.add(path)
        else:
            abspath = check_dirs(path)
            if abspath:
                abspaths.add(abspath)
            else:
                notfound.add(path)
    if ErrorType:
        return abspaths
    else:
        return abspaths, notfound
