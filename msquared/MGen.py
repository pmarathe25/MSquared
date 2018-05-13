from msquared._utils import _str_to_list, _locate_files_in_paths, _find_included_files, _find_file_in_list, _prompt_user_disambiguate_dependency
from typing import Dict, List, Set, Union
from datetime import datetime
import os
from stat import S_IWRITE, S_IREAD, S_IRGRP, S_IROTH

class MGen(object):
    def __init__(self, project_dirs: List[str] = [], build_dir: str = "build"):
        project_dirs = _str_to_list(project_dirs)
        # Project options
        self._project_dirs: List[str] = project_dirs
        # This is populated just before generation.
        self._project_files: List[str] = []
        # Temporary storage - create the directory during generation if it does not exist.
        self.build_dir: str = build_dir
        self.temporary_files: List[str] = [build_dir + "/*"]
        # Custom Targets map a target directly to a makefile string.
        self.custom_targets: Dict[str, str] = {}
        self.phony_targets: List[str] = ["clean"]
        # Maintains a mapping of targets to their constituent source files.
        self.targets: Dict[str, List[str]] = {}
        # Compiler options
        self.cc = "g++ "
        self.cflags: str = "-fPIC -c "
        self.lflags: str = ""

    def __getitem__(self, index):
        return self.targets[index]

    def _get_makefile_header():
        return "# Automatically generated Makefile. DO NOT MODIFY.\n# Generated on " + str(datetime.today()) + '\n\n'

    # Figures out whether a dependency is internal or not.
    def _check_is_internal_dependency(self, filename: str) -> Union[str, None]:
        matching_project_files: List[str] = _find_file_in_list(filename, self._project_files)
        matched_file: str = None
        if len(matching_project_files) == 1:
            # Found a matching file in the project!
            matched_file = matching_project_files[0]
        elif len(matching_project_files) > 1:
            # If there is more than one match, prompt user to disambiguate.
            matched_file = _prompt_user_disambiguate_dependency(filename, matching_project_files)
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

    def set_compiler(self, compiler: str) -> None:
        self.cc = compiler

    def add_flags(self, flags: str) -> None:
        self.add_cflags(flags)
        self.add_lflags(flags)

    def add_cflags(self, flags: str) -> None:
        self.cflags += flags + " "

    def add_lflags(self, flags: str) -> None:
        self.lflags += flags + " "

    def add_executable(self, exec_name: str, source_files: List[str], clean: bool = False) -> None:
        if clean:
            self.add_clean_files(exec_name)
        source_files = _str_to_list(source_files)
        self.targets[exec_name] = source_files

    # Libraries are processed before executables.
    def add_library(self, lib_name: str, source_files: List[str], clean: bool = False) -> None:
        if clean:
            self.add_clean_files(exec_name)
        source_files = _str_to_list(source_files)
        self.targets[lib_name] = source_files

    def add_custom_target(self, target_name: str, dependencies: List[str] = [],
        command: List[str] = [], phony: bool = True) -> None:
        if phony:
            self.phony_targets.append(target_name)
        command = _str_to_list(command)
        dependencies = _str_to_list(dependencies)
        self.custom_targets[target_name] = target_name + ": " + " ".join(dependencies) \
            + "\n\t" + "\n\t".join(command) + "\n\n"

    def add_clean_files(self, files: List[str] = []) -> None:
        files = _str_to_list(files)
        self.temporary_files.extend(files)

    def generate(self) -> str:
        def process_phony_targets() -> str:
            makefile: str = ""
            if self.phony_targets:
                makefile += ".PHONY:"
                # Declare targets as being phony
                for phony_target in self.phony_targets:
                    makefile += " " + phony_target
                makefile += "\n\n"
            return makefile

        def process_real_targets() -> str:
            makefile: str = ""
            for target, sources in self.targets.items():
                # Need to create an intermediate .o target for each source file.
                obj_files: List[str] = []
                for source_file in sources:
                    # Generate the corresponding object file by replacing any extension with '.o'.
                    object_name = self.build_dir + '/' + os.path.splitext(os.path.basename(source_file))[0] + ".o"
                    obj_files.append(object_name)
                    # And then figure out #include dependencies.
                    dependencies = self._internal_dependencies(source_file)
                    # Omit first dependency (Original source file)
                    include_paths = set([os.path.dirname(dep) for dep in dependencies[1:]])
                    # Target.
                    makefile += object_name + ": " + " ".join(dependencies) + '\n'
                    # Now the actual compilation step - make sure headers are visible!
                    makefile += '\t' + self.cc + self.cflags + source_file + " -o " \
                        + object_name + " -I" + " -I".join(include_paths) + '\n\n'
                # Now that the objects exist, we can add the executable itself.
                makefile += target + ": " + " ".join(obj_files) + '\n'
                # And compile to executable.
                makefile += '\t' + self.cc + self.lflags + " ".join(obj_files) + " -o " + target + '\n\n'
            return makefile

        def process_clean_targets() -> str:
            makefile: str = ""
            return "clean:\n\trm -rf " + " ".join(self.temporary_files) + '\n\n'

        def process_custom_targets() -> str:
            makefile: str = ""
            for target, make_target in self.custom_targets.items():
                makefile += make_target
            return makefile

        # Find out what's in the project now.
        self._project_files = _locate_files_in_paths(self._project_dirs)
        # Create build directory if it doesn't exist.
        os.makedirs(self.build_dir, exist_ok=True)
        # Generate makefile.
        makefile: str = MGen._get_makefile_header()
        # Phony targets should be at the top of the makefile.
        makefile += process_phony_targets()
        # Handle libraries and executables.
        makefile += process_real_targets()
        # Clean target
        makefile += process_clean_targets()
        # And finally custom targets.
        makefile += process_custom_targets()
        # Done
        return makefile

    def write(self, filename: str) -> None:
        makefile = self.generate()
        # Unlock file.
        os.chmod(filename, S_IWRITE|S_IRGRP|S_IROTH)
        with open(filename, "w") as outf:
            # Write to output file.
            outf.write(makefile)
        # Mark the file as read-only so it's not accidentally modified.
        os.chmod(filename, S_IREAD|S_IRGRP|S_IROTH)
