from msquared._utils import _handle_str, _locate_files, _find_included_files
from typing import Dict, List, Set, Union
import os

class MGen(object):
    def __init__(self, project_dirs: List[str] = [], build_dir: str = "build"):
        project_dirs = _handle_str(project_dirs)
        # Targets
        # TODO:
        # self.custom_targets: Dict[str, str] = {}
        self.temporary_files: List[str] = [build_dir + "/*"]
        self.phony_targets: List[str] = ["clean"]
        # Maintains a mapping of executables to their constituent source files.
        self.executables: Dict[str, List[str]] = {}
        # Project options
        self.build_dir: str = build_dir
        self._project_dirs: List[str] = project_dirs
        self._project_files: List[str] = _locate_files(self._project_dirs)
        # Compiler options
        self.cc = "g++ "
        self.cflags: str = "-fPIC -c "
        self.lflags: str = ""

    def __getitem__(self, index):
        return self.targets[index]

    # Figures out whether a dependency is internal or not.
    def _check_is_internal_dependency(self, filename: str) -> Union[str, None]:
        # If there are multiple matching files, the user needs to specify which one to use.
        def prompt_user_disambiguate_dependency(self, filename: str, matching_project_files: List[str]) -> str:
            matched_file: str = None
            # Make sure that the selected file is actually in the project.
            matched_file = input("For dependency " + filename + ", found: "
            + str(matching_project_files) + ". Please choose one.\n>>> ")
            while len(self.find_project_file(matched_file)) != 1:
                matched_file = input("ERROR: '" + matched_file + "' not found in project. "
                "Please enter a valid file name.\n>>> ")
            return matched_file

        matching_project_files: List[str] = self.find_project_file(filename)
        matched_file: str = None
        if len(matching_project_files) == 1:
            # Found a matching file in the project!
            matched_file = matching_project_files[0]
        elif len(matching_project_files) > 1:
            # If there is more than one match, prompt user to disambiguate.
            matched_file = prompt_user_disambiguate_dependency(self, filename, matching_project_files)
        return matched_file

    # Figures out what internal headers (i.e. in project_dirs) a source file depends on.
    def _internal_dependencies(self, source_file: str) -> List[str]:
        # Keep track of dependencies found so far.
        dependencies: List[str] = [source_file]
        # For each dependent file, scan through and see if its dependencies are located in the project.
        for filename in dependencies:
            nested_dependencies: List[str] = _find_included_files(filename)
            for nested_filename in nested_dependencies:
                # For each of these, check if it is in the project.
                # If so, append to the list of dependencies to look through.
                new_dependency = self._check_is_internal_dependency(nested_filename)
                if new_dependency and new_dependency not in dependencies:
                    # Don't check duplicates repeatedly.
                    dependencies.append(new_dependency)
        # Return a list of unique dependencies.
        return dependencies

    # Given the name/path of a file, find potential matches in this project.
    def find_project_file(self, filename: str) -> List[str]:
        # For paths, get relative path.
        filename = os.path.relpath(filename) if '/' in filename else filename

        print(filename)

        possible_matches: List[str] = []
        for project_filename in self._project_files:
            if filename == project_filename or filename == project_filename.split('/')[-1]:
                # Either the path matches exactly, or the file name patches exactly.
                possible_matches.append(project_filename)
        return possible_matches

    def set_compiler(self, compiler: str) -> None:
        self.cc = compiler

    def add_flags(self, flags: str) -> None:
        self.add_cflags(flags)
        self.add_lflags(flags)

    def add_cflags(self, flags: str) -> None:
        self.cflags += " " + flags

    def add_lflags(self, flags: str) -> None:
        self.lflags += " " + flags

    def add_executable(self, exec_name: str, source_files: List[str]):
        source_files = _handle_str(source_files)
        self.executables[exec_name] = source_files

    def clean_files(self, files: List[str] = []):
        files = _handle_str(files)
        self.temporary_files.extend(files)

    def generate(self) -> str:
        makefile: str = ""
        if self.phony_targets:
            makefile += ".PHONY:"
            # Declare targets as being phony
            for phony_target in self.phony_targets:
                makefile += " " + phony_target
            makefile += '\n'
        # First, handle libraries.

        # Then executables.
        for target, sources in self.executables.items():
            # Need to create an intermediate .o target for each source file.
            for source_file in sources:
                print("Finding deps for " + source_file)
                dependencies = self._internal_dependencies(source_file)
                print(dependencies)

        # Clean target
        makefile += "clean:\n\trm -rf " + " ".join(self.temporary_files)
        # And finally custom targets.

        # Done
        return makefile

    def write(self, filename: str) -> None:
        makefile = self.generate()
        with open(filename, "w") as outf:
            # Write to output file.
            outf.write(makefile)
