# from msquared._utils import _convert_to_list, _expand_glob_list
from typing import List, Set
from msquared import _utils as utils


class Target(object):
    NEWLINE = '\n'

    def __init__(self, name: str, deps: List[str], command: str):
        self.name = name
        self.deps = deps
        self.command = command

    def __str__(self):
        return f"{self.name}:{utils._prefix_join(self.deps)}\n\t{self.command}{Target.NEWLINE if self.command else ''}"
