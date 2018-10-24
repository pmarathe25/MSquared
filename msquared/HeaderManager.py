import re
from msquared import utils
from typing import Dict, Set

class HeaderManager(object):
    def __init__(self, header_dirs, logger):
        self.header_dirs: Set[str] = header_dirs
        self.logger: Logger = logger
        self.header_cache: Dict[str, Set[str]] = {}

    # Given a file, recursively locates all headers in that file.
    def locate_headers(self, filename):
        # First check the cache, so we don't recurse unnecessarily.
        if filename in self.header_cache:
            self.logger.debug(f"Found {filename} in header cache. Using headers: {self.header_cache[filename]}")
            return self.header_cache[filename]
        # Find the headers in this file.
        headers = self.find_included_files(filename)
        headers, notfound = utils.locate_paths(headers, self.header_dirs, self.logger)
        if notfound:
            self.logger.warning(f"For {filename}, assuming {notfound} are external headers. If this is incorrect, please set project_include_dirs correctly (currently set to {self.header_dirs}).")
        # Next find the headers contained within those headers.
        all_headers = set() | headers
        for header in headers:
            self.logger.debug(f"For {filename}, recursing through {header}")
            all_headers |= self.locate_headers(header)
        # Cache
        self.logger.debug(f"Adding entry to header cache: {filename}: {all_headers}")
        self.header_cache[filename] = all_headers
        return all_headers

    # Finds all #include's in a file.
    def find_included_files(self, filename: str) -> Set[str]:
        with open(filename, 'r') as file:
            # Match includes of the form #include <.*> and #include ".*" excluding commented out lines.
            return set(re.findall('(?:(?<!\/\/\s))#include [<"]([^>"]*)[>"]', file.read()))
