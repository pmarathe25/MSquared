from msquared._utils import _handle_str, _locate_files
from typing import Dict, List
import glob

class MGen(object):
    def __init__(self, project_dirs: List[str] = [], build_dir: str = "build/*"):
        project_dirs = _handle_str(project_dirs)
        self.targets: Dict[str, str] = {}
        self.phony_targets: List[str] = []
        self.cc = "g++ "
        self.cflags: str = "-fPIC -c "
        self.lib_lflags: str = "-shared "
        self.exec_lflags: str = ""
        self.build_dir: str = build_dir
        self._project_dirs: List[str] = project_dirs
        self._project_files: List[str] = _locate_files(self._project_dirs)

    def __getitem__(self, index):
        return self.targets[index]

    # Figures out what internal headers (i.e. in project_dirs) a source file depends on.
    def _internal_header_dependencies(source_file: str):
        pass

    def set_compiler(self, compiler: str) -> None:
        self.cc = compiler

    def add_flags(self, flags: str) -> None:
        self.add_cflags(flags)
        self.add_lib_lflags(flags)
        self.add_exec_lflags(flags)

    def add_cflags(self, flags: str) -> None:
        self.cflags += " " + flags

    def add_lib_lflags(self, flags: str) -> None:
        self.lib_lflags += " " + flags

    def add_exec_lflags(self, flags: str) -> None:
        self.exec_lflags += " " + flags

    def add_executable(self, exec_name: str, dependencies: List[str]):
        dependencies = _handle_str(dependencies)
        pass

    def add_clean(self, files: List[str] = []):
        files = _handle_str(files)
        self.targets["clean"] = "rm -r " + self.build_dir + " " + " ".join(files)
        self.phony_targets.append("clean")

    def generate(self, filename: str):
        makefile: str = ""
        if self.phony_targets:
            makefile += ".PHONY:"
            # Declare targets as being phony
            for phony_target in self.phony_targets:
                makefile += " " + phony_target
            makefile += '\n'
        # Create targets
        for target_name, target_value in self.targets.items():
            makefile += '\n' + target_name + '\n\t' + target_value
        # DEBUG:
        print(makefile)
        # Write to output file.
        with open(filename, "w") as outf:
            outf.write(makefile)
