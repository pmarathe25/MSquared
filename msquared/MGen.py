from msquared._utils import _handle_str
from typing import Dict, List

def test_func():
    pass

class MGen(object):
    def __init__(self, build_dir: str = "build/"):
        self.targets: Dict[str, str] = {}
        self.phony_targets: List(str) = []
        self.global_cflags: str = "-fPIC -c"
        self.global_lib_lflags: str = "-shared"
        self.global_exec_lflags: str = ""
        self.build_dir: str = build_dir

    def __getitem__(self, index):
        return self.targets[index]

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
        self.targets["clean"] = "rm -r " + self.build_dir + " " + " ".join(files)
        self.phony_targets.append("clean")
        pass

    def generate(self, filename: str):
        makefile: str = ""
        for target_name, target_value in self.targets.items():
            makefile += target_name + '\n\t' + target_value
        print(makefile)
        pass
