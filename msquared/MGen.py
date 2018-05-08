from msquared._utils import _handle_str
from typing import Dict, List

def test_func():
    pass

class MGen(object):
    def __init__(self, build_dir: str = "build/"):
        self.targets : Dict[str, List(str)]
        self.phony_targets : List
        self.global_cflags = "-fPIC -c -march=native"
        self.global_lib_lflags = "-shared -march=native"
        self.global_exec_lflags = "-march=native"
        self.build_dir = build_dir

    def __getitem__(self, index):
        return self.targets[index]

    """ Functions for generating targets_contents. """
    def add_flags(self, flags: str) -> None:
        self.add_cflags(flags)
        self.add_lib_lflags(flags)
        self.add_exec_lflags(flags)

    def add_cflags(self, flags: str) -> None:
        self.global_cflags += " " + flags

    def add_lib_lflags(self, flags: str) -> None:
        self.global_lib_lflags += " " + flags

    def add_exec_lflags(self, flags: str) -> None:
        self.global_exec_lflags += " " + flags

    def add_executable(self, exec_name: str, dependencies: List[str]):
        dependencies = _handle_str(dependencies)
        pass

    def add_clean(self, files: List[str] = []):
        files = _handle_str(files)
        pass

    def generate(self, filename: str):
        print(self.targets)
        pass
