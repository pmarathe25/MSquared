from msquared._utils import _convert_to_list, _ends_with, _find_included_files, _expand_glob_list, _suffix, _disambiguate
from msquared.Target import *
from stat import S_IWRITE, S_IREAD, S_IRGRP, S_IROTH
from typing import Dict, List, Set, Union
from datetime import datetime
from enum import IntEnum
import glob
import os

class FileType(IntEnum):
    SOURCE = 0
    OBJECT = 1
    SHARED_OBJECT = 2

def _file_type(filename: str) -> FileType:
    if os.path.splitext(filename)[1] == ".so":
        return FileType.SHARED_OBJECT
    elif os.path.splitext(filename) == ".o":
        return FileType.OBJECT
    return FileType.SOURCE

class MGen(object):
    def __init__(self, project_dirs: Union[str, List[str]] = [], build_dir: str = "build/"):
        self.project_dirs = _convert_to_list(project_dirs)
        self.build_dir = build_dir
        # Compiler settings
        self.cc = "g++"
        self.cflags = ["-fPIC", "-c"]
        self.lflags = ""
        # Targets
        self.targets: Dict[str, List[str]] = {}
        self.sources: Set[str] = set()

    def _object_name(self, filename: str) -> str:
        return _suffix(self.build_dir, '/') + os.path.splitext(os.path.basename(filename))[0] + ".o"

    # Dependencies can be globs.
    def add_target(self, name: str, deps: Union[str, List[str]]):
        deps: List[str] = list(_expand_glob_list(_convert_to_list(deps)))
        # For source files in deps, change to object files.
        for index, dep in enumerate(deps):
            if _file_type(dep) == FileType.SOURCE:
                self.sources.add(dep)
                deps[index] = self._object_name(dep)
        self.targets[name] = deps
        # DEBUG:
        print("Added Target")
        print(self.targets[name])
        print("Updating source files")
        print(self.sources)

    # def _push_dependencies(self, dependencies: List[str], makefile_stack: List[str], pushed_deps: Set[str] = set()):
    #     for dep in dependencies:
    #             # First push it's dependencies, then the target itself.
    #             if dep in self.targets[dep] and self.targets[dep]:
    #                 self._push_dependencies(self.targets[dep], makefile_stack, pushed_deps)
    #             if dep not in pushed_deps:
    #                 self._push_target(dep, self.targets[dep], makefile_stack)
    #                 pushed_deps.add(dep)
    #
    # def _push_target(self, name: str, dependencies: List[str], makefile_stack: List[str]):
    #     makefile_stack.append(f"{name}: {' '.join(dependencies)}")

    def _find_in_project(self, filename: str):
        found_files: List[str] = []
        for project_dir in self.project_dirs:
            found_files.extend(glob.glob(os.path.join(project_dir, '**', filename), recursive=True))
        return found_files

    def _find_headers(self, header: str, cache: Dict[str, Set[str]]):
        # Make sure we know which header we're looking at
        header = _disambiguate(self._find_in_project(header))
        # DEBUG:
        # if header:
            # print(f"\tFor header {header} found candidates {self._find_in_project(header)}")
            # print(f"\t\tFor header {header} using {header}")
        if header in cache:
            # DEBUG:
            # print(f"\tFor header {header} hit cache!")
            return cache[header]
        elif header:
            all_headers = set([header])
            all_include_paths = set([os.path.dirname(header)])
            for included_file in _find_included_files(header):
                # Recurse through all dependencies to find headers and their respective include paths.
                headers, include_paths = self._find_headers(included_file, cache)
                all_headers.update(headers)
                all_include_paths.update(include_paths)
            # Add to cache before returning and find required include paths too.
            cache[header] = (all_headers, all_include_paths)
            return cache[header]
        return (set(), set())

    def _push_source(self, source: str, header_cache: Dict[str, Set[str]], makefile_stack: List[str]):
        headers, include_paths = self._find_headers(source, header_cache)
        # DEBUG:
        # print(f"For source {source} found headers: {headers}")
        object = self._object_name(source)
        makefile_stack.append(f"{object}: {' '.join(headers)}\n"
            f"\t{self.cc} {source} {' '.join(self.cflags)} -o {object} {' -I'.join(include_paths)}\n")

    def generate(self):
        makefile_stack: List[str] = ["MAKEFILE START"]
        # First compile all source files to objects.
        header_cache = {}
        for source in self.sources:
            self._push_source(source, header_cache, makefile_stack)
        # DEBUG:
        print(f"Header Cache: {header_cache}")
        # for name, dependencies in self.targets.items():
        #     self._push_dependencies(dependencies, makefile_stack)
        return '\n'.join(makefile_stack)

# class MGen(object):
#     def __init__(self, project_dirs: List[str] = [], build_dir: str = "build"):
#         project_dirs = _convert_to_list(project_dirs)
#         # Project options
#         self._project_dirs: List[str] = project_dirs
#         # This is populated just before generation.
#         self._project_files: List[str] = []
#         # Temporary storage - create the directory during makefile generation if it does not exist.
#         self.build_dir: str = build_dir
#         self.temporary_files: List[str] = []
#         # Custom Targets map a target directly to a makefile string.
#         self.custom_targets: Dict[str, str] = {}
#         self.phony_targets: List[str] = ["clean"]
#         # Maintains a mapping of targets to their constituent source files.
#         # Also keeps track of the type of the target.
#         self.targets: Dict[str, Target] = {}
#         # Compiler options
#         self.cc = "g++ "
#         self.cflags: str = "-fPIC -c "
#         self.lflags: str = ""
#         # Keep track of internal dependency lists so we don't incur Disk I/O every time.
#         self._internal_dependencies: Dict[str, Set[str]] = {}
#
#     def __getitem__(self, index):
#         return self.targets[index]
#
#     def _get_makefile_header() -> str:
#         return "# Automatically generated by msquared.MGen on "  + str(datetime.today()) + ".\n# DO NOT MODIFY.\n\n"
#
#     # Figures out what internal headers (i.e. in project_dirs) a source file depends on.
#     def _find_dependencies(self, source_file: str) -> List[str]:
#         # Figures out whether a dependency is internal or not.
#         def _check_is_internal_dependency(dependency: str, source_file: str) -> Union[str, None]:
#             matching_project_files: List[str] = _find_file_in_list(dependency, self._project_files)
#             matched_file: str = None
#             if len(matching_project_files) == 1:
#                 # Found a matching file in the project!
#                 matched_file = matching_project_files[0]
#             elif len(matching_project_files) > 1:
#                 # If there is more than one match, prompt user to disambiguate.
#                 matched_file = _prompt_user_disambiguate_dependency(dependency, matching_project_files, source_file)
#             return matched_file
#
#         if source_file in self._internal_dependencies:
#             return self._internal_dependencies[source_file]
#         # Not cached, compute dependencies.
#         all_dependencies: Set[str] = set()
#         dependencies: List[str] = _find_included_files(source_file)
#         for dependency in dependencies:
#             # If this isn't an internal dependency (or already added), we don't care about it.
#             dependency = _check_is_internal_dependency(dependency, source_file)
#             if dependency and dependency not in all_dependencies:
#                 # Otherwise, add this dependency and its children.
#                 all_dependencies.add(os.path.abspath(dependency))
#                 all_dependencies.update(self._find_dependencies(dependency))
#         # Cache and return.
#         self._internal_dependencies[source_file] = all_dependencies
#         return self._internal_dependencies[source_file]
#
#     """API Functions"""
#     def set_compiler(self, compiler: str) -> None:
#         self.cc = compiler
#         return self
#
#     def add_flags(self, flags: str) -> None:
#         self.add_cflags(flags)
#         self.add_lflags(flags)
#         return self
#
#     def add_cflags(self, flags: str) -> None:
#         self.cflags += flags + " "
#         return self
#
#     def add_lflags(self, flags: str) -> None:
#         self.lflags += flags + " "
#         return self
#
#     def register_executable(self, exec_name: str, source_files: List[str], clean: bool = False, libraries: List[str] = []) -> None:
#         exec_name = os.path.abspath(exec_name)
#         if clean:
#             self.register_clean_files(exec_name)
#         libraries: List[str] = _convert_to_list(libraries)
#         shared_obj_files: Set[str] = set()
#         lib_flags: str = ""
#         for lib in libraries:
#             lib = lib.strip()
#             # For .so's, link normally. Otherwise, conditionally prepend with -l.
#             if ".so" in lib:
#                 shared_obj_files.add(os.path.abspath(lib))
#             else:
#                 lib_flags += _prepend("-l", lib) + " "
#         # Not setting obj_files=set() breaks everything.
#         self.targets[exec_name] = Target(type=TargetType.EXECUTABLE, sources=source_files, obj_files=set(), shared_obj_files=shared_obj_files, post_flags=lib_flags)
#         return self
#
#     def register_library(self, lib_name: str, source_files: List[str], clean: bool = False) -> None:
#         lib_name = os.path.abspath(lib_name)
#         pre_flags = "-shared " if _ends_with(lib_name, ".so") else ""
#         if clean:
#             self.register_clean_files(lib_name)
#         self.targets[lib_name] = Target(TargetType.LIBRARY, source_files, obj_files=set(), pre_flags=pre_flags)
#         return self
#
#     def register_custom_target(self, target_name: str, commands: List[str] = [], phony: bool = True, dependencies: List[str] = []) -> None:
#         if phony:
#             self.phony_targets.append(target_name)
#         commands = _convert_to_list(commands)
#         dependencies = [os.path.abspath(dep) for dep in _convert_to_list(dependencies)]
#         self.custom_targets[target_name] = target_name + ": " + " ".join(dependencies) \
#             + "\n\t" + "\n\t".join(commands) + ("\n\n" if commands else "\n")
#         return self
#
#     # Supports globs (expanded during generation).
#     def register_clean_files(self, files: List[str] = []) -> None:
#         files = _convert_to_list(files)
#         self.temporary_files.extend(files)
#         return self
#
#     # Where the bulk of the work happens.
#     def generate(self) -> str:
#         def add_phony_targets(makefile: str) -> str:
#             if self.phony_targets:
#                 makefile += ".PHONY:"
#                 # Declare targets as being phony
#                 for phony_target in self.phony_targets:
#                     makefile += " " + phony_target
#                 makefile += "\n\n"
#                 return None
#
#         def add_real_targets(makefile: str) -> str:
#             object_files: List[str] = []
#             # Keep a mapping of what the final targets look like. In the order INTERMEDIATE, LIBRARY, EXECUTABLE.
#             final_targets: List[Dict[str, str]] = [{}, {}, {}]
#             # target here refers to an object of the Target class.
#             for target_name, target in self.targets.items():
#                 # Need to create an intermediate .o target for each source file.
#                 for source_file in target.sources:
#                     # Generate the corresponding object file by replacing any extension with '.o'.
#                     object_name = self.build_dir + '/' + os.path.splitext(os.path.basename(source_file))[0] + ".o"
#                     object_name = os.path.abspath(object_name)
#                     target.obj_files.add(object_name)
#                     object_files.append(object_name)
#                     # No need for duplicate intermediate objects.
#                     if object_name not in final_targets[TargetType.INTERMEDIATE]:
#                         # And then figure out #include dependencies.
#                         dependencies = self._find_dependencies(source_file)
#                         print(source_file + " depends on " + str(dependencies))
#                         include_paths = set([os.path.dirname(dep) for dep in dependencies])
#                         # Make sure headers are visible with -I!
#                         final_targets[TargetType.INTERMEDIATE][object_name] = object_name + ": " + source_file + " " \
#                             + " ".join(dependencies) + "\n\t" + self.cc + self.cflags + source_file \
#                             + " -o " + object_name + (" -I" + " -I".join(include_paths) if include_paths else "")  + '\n\n'
#                 # Now that the objects exist, we can add the executable/lib itself.
#                 if target_name not in final_targets[target.type]:
#                     final_targets[target.type][target_name] = target_name + ": " + " ".join(target.obj_files) + " " \
#                         + " ".join(target.shared_obj_files) + "\n\t" \
#                         + self.cc + target.pre_flags + self.lflags + " ".join(target.obj_files) + " " \
#                         + " ".join(target.shared_obj_files) + " -o " + target_name + " " + target.post_flags + '\n\n'
#             # Now that we have all the targets, order them properly i.e. INTERMEDIATE, LIBRARY, EXECUTABLE.
#             for target_dict in final_targets:
#                 for target_name, makefile_string in target_dict.items():
#                     makefile += makefile_string
#             return object_files
#
#         def add_clean_targets(makefile: str, temporary_files: List[str]) -> str:
#             makefile: str = ""
#             temporary_files = _expand_glob_list(temporary_files)
#             # Use root privilege if any of the temporary_files cannot be written to.
#             sudo = "sudo " if any([not os.access(os.path.dirname(temp_file), os.W_OK) for temp_file in temporary_files]) else ""
#             makefile += "clean:\n\t" + sudo + "rm -rf " + " ".join(temporary_files) + '\n\n'
#             return None
#
#         def add_custom_targets(makefile: str) -> str:
#             for target, make_target in self.custom_targets.items():
#                 makefile += make_target
#             return None
#
#         # Find out what's in the project now.
#         self._project_files = _locate_files_in_paths(self._project_dirs)
#         # Create build directory if it doesn't exist.
#         os.makedirs(self.build_dir, exist_ok=True)
#         # Generate makefile.
#         makefile: List[str] = [MGen._get_makefile_header()]
#         # Phony targets should be at the top of the makefile.
#         add_phony_targets(makefile)
#         # Handle libraries and executables. This will also update temporary_files.
#         object_files = add_real_targets(makefile)
#         # Clean target
#         add_clean_targets(makefile, object_files + self.temporary_files)
#         # And finally custom targets.
#         add_custom_targets(makefile)
#         # Done
#         return "".join(makefile)
#
#     def write(self, filename: str) -> None:
#         makefile = self.generate()
#         # Unlock file.
#         if os.path.isfile(filename):
#             os.chmod(filename, S_IWRITE|S_IRGRP|S_IROTH)
#         with open(filename, "w") as outf:
#             # Write to output file.
#             outf.write(makefile)
#         # Mark the file as read-only so it's not accidentally modified.
#         os.chmod(filename, S_IREAD|S_IRGRP|S_IROTH)
