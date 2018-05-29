# from msquared._utils import _convert_to_list, _expand_glob_list
from typing import List, Set
from msquared import _utils as utils


class Target(object):
    def __init__(self, name: str, deps: List[str], command: List[str]):
        self.name = name
        self.deps = deps
        # Don't create unnecessary whitespace.
        self.command = utils._prefix_join(command, '\n\t') if ''.join(command).strip() else ""

    def __str__(self):
        return f"{self.name}:{utils._prefix_join(self.deps)}{self.command}\n"
