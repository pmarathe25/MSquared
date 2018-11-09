from msquared import utils
from msquared.Logger import Logger
from msquared.Target import Target, MakefileTarget
from msquared.Compilers import *
from msquared.HeaderManager import HeaderManager
from typing import Dict, List, Set
from datetime import datetime
import inspect
import enum
import os
import copy

"""
API Functions
"""
def add_prefix(prefix, objs):
    """
    Adds a prefix to each element of a list.

    Args:
        prefix (object): The prefix to prepend to each element of the list.
        objs (List[object]): The list of elements to prepend.

    Returns:
        List[object]: A new list with the prefix prepended.
    """
    return [prefix + obj for obj in objs]

def add_suffix(objs, suffix):
    """
    Adds a suffix to each element of a list.

    Args:
        objs (List[object]): The list of elements to append.
        suffix (object): The suffix to append to each element of the list.

    Returns:
        List[object]: A new list with the suffix appended.
    """
    return [suffix + obj for obj in objs]

def wrap(prefix, objs, suffix):
    """
    Adds a prefix and suffix to each element of a list.

    Args:
        prefix (object): The prefix to prepend to each element of the list.
        objs (List[object]): The list of elements to append.
        suffix (object): The suffix to append to each element of the list.

    Returns:
        List[object]: A new list with the suffix appended.
    """
    return [prefix + obj + suffix for obj in objs]

class MGen(object):
    """
    Internal Functions
    """
    def _get_makefile_header() -> str:
        return "# Automatically generated by msquared.MGen on " + str(datetime.today()) + ".\n# DO NOT MODIFY."

    # The key difference between project_include_dirs and include_dirs is that include_dirs headers are still treated as
    # being external to the project i.e. they are not scanned recursively for dependencies.
    def __init__(self, project_source_dirs=set(["."]), project_include_dirs=set(), build_dir="build", compiler=GCC, cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), logger_severity=Logger.Severity.INFO):
        # Logging
        self.logger: Logger = Logger(logger_severity)

        # The assumption is that the caller of the init function is the MGen file for the build.
        self.root_dir = os.path.abspath(os.path.dirname(inspect.stack()[1][0].f_code.co_filename))
        self.logger.info(f"Using root directory: {self.root_dir}")

        self.project_source_dirs: Set[str] = utils.locate_paths(project_source_dirs, self.root_dir, self.logger, ErrorType=FileNotFoundError)
        self.logger.debug(f"Using project source directories: {self.project_source_dirs}")

        # Only a single build directory should be found, and it should not be an existing directory
        # if provided as an absolute path. This way, '/' can't accidentally be a build directory.
        self.set_build_dir(build_dir)

        # Global compiler options
        self.compiler: BaseCompiler = compiler
        self.cflags: Set[str] = utils.convert_to_set(cflags) if cflags else compiler.default_flags
        project_include_dirs: Set[str] = utils.locate_paths(project_include_dirs, self.root_dir, self.logger, ErrorType=FileNotFoundError)
        self.logger.debug(f"Using project include directories: {project_include_dirs}")
        self.include_dirs: Set[str] = utils.convert_to_set(include_dirs) | project_include_dirs
        self.lflags: Set[str] = utils.convert_to_set(lflags) if lflags else compiler.default_flags
        self.link_dirs: Set[str] = utils.convert_to_set(link_dirs)

        # Keep track of user-defined targets.
        self.release_targets: List[Target] = []
        self.debug_targets: List[Target] = []
        self.install_targets: List[Target] = []
        # Use a header manager.
        self.header_manager = HeaderManager(project_include_dirs, self.logger)
        # Map library names to the exact name used for linking them. When a library is added, or any target
        # with a library dependency is added, this is updated.
        self.library_registry: Dict[str, str] = {}

    def _generate_target(self, name: str, sources: Set[str], libraries: Set[str], cflags: Set[str], include_dirs: Set[str], lflags: Set[str], link_dirs: Set[str], compiler: BaseCompiler, output_directory: str, install_dir: str) -> Target:
        # Add global options to each executable. This makes the Targets returned to the user complete.
        # Sources and header dependencies.
        sources = utils.locate_paths(sources, self.project_source_dirs, self.logger, FileNotFoundError)
        source_map = {}
        for source in sources:
            source_map[source] = self.header_manager.locate_headers(source)
        # Compiler settings.
        libraries = utils.convert_to_set(libraries)
        cflags = utils.convert_to_set(cflags) | self.cflags
        include_dirs = utils.convert_to_set(include_dirs) | self.include_dirs
        lflags = utils.convert_to_set(lflags) | self.lflags
        link_dirs = utils.convert_to_set(link_dirs) | self.link_dirs
        compiler = compiler if compiler else self.compiler
        output_directory = output_directory if output_directory else self.build_dir
        install_dir = os.path.join(self.root_dir, install_dir) if install_dir and not os.path.isabs(install_dir) else install_dir
        # Add release target.
        path = os.path.abspath(os.path.join(output_directory, name))
        target = Target(name, path, source_map, libraries, cflags, include_dirs, lflags, link_dirs, compiler, logger=self.logger, obj_out_dir=os.path.join(self.build_dir, "objs"), install_dir=install_dir)
        self.release_targets.append(target)
        return target

    """
    API Functions
    """
    # TODO: Update all docstrings here.
    def set_build_dir(self, build_dir: str) -> None:
        if os.path.isabs(build_dir):
            if os.path.exists(build_dir):
                self.logger.error(f"Directory {build_dir} already exists, will not use as build directory.", OSError)
            self.build_dir = build_dir
        else:
            self.build_dir = os.path.join(self.root_dir, build_dir)
        self.logger.debug(f"Using project build directory: {self.build_dir}")

    def add_executable(self, name: str, sources=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), compiler=None, output_directory=None, install_directory=None) -> Target:
        """
        Adds an executable to be generated based on the specified source files.

        Args:
            name (str): The name of the executable.
            sources (Set[str]): A set of source files used to create the executable.
            libraries (Set[str]): Any additional libraries to link against. These can include libraries defined by `add_library`.
            cflags (Set[str]): Flags to use while compiling constituent source files.
            include_dirs (Set[str]): Include directories for source files.
            lflags (Set[str]): Flags to use while linking constituent object files.
            link_dirs (Set[str]): Link directories for libraries.
            compiler (BaseCompiler): The compiler to use.

        Returns:
            Target: A new target representing the executable.
        """
        return self._generate_target(name, sources, libraries, cflags, include_dirs, lflags, link_dirs, compiler, output_directory, install_directory)

    def add_library(self, name: str, sources=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), compiler=None, output_directory=None, install_directory=None) -> Target:
        """
        Adds a library to be generated based on the specified source files.

        Args:
            name (str): The name of the library.
            sources (Set[str]): A set of source files used to create the library.
            libraries (Set[str]): Any additional libraries to link against. These can include libraries defined by `add_library`.
            cflags (Set[str]): Flags to use while compiling constituent source files.
            include_dirs (Set[str]): Include directories for source files.
            lflags (Set[str]): Flags to use while linking constituent object files.
            link_dirs (Set[str]): Link directories for libraries.
            compiler (BaseCompiler): The compiler to use.

        Returns:
            Target: A new target representing the library.
        """
        target = self._generate_target(name, sources, libraries, cflags, include_dirs, lflags, link_dirs, compiler, output_directory, install_directory)
        # Add the shared flag.
        target.lflags.add(target.compiler.shared)
        # Register this library.
        self.library_registry[target.name] = target.path
        return target

    def add_install(self, path: str, install_directory: str) -> Target:
        # FIXME: This may cause name collisions for files with the same name but different paths.
        name = os.path.basename(path)
        path = os.path.join(self.root_dir, path) if not os.path.isabs(path) else path
        if not os.path.exists(path):
            self.logger.error(f"Could not find {path}", FileNotFoundError)
        target = Target(name=name, path=path, install_dir=install_directory)
        self.install_targets.append(target)
        return target

    def generate(self, human_readable_object_names=False):
        """
        Generates a Makefile.
        """
        # Walk over all the targets. For each one, we add an intermediate target for each source file.
        build_targets = set()
        phony_targets = []
        install_targets = []
        uninstall_targets = []
        for target in self.release_targets + self.debug_targets + self.install_targets:
            build_targets |= utils.convert_to_set(target.generate_build_targets(self.library_registry, human_readable_object_names))
            phony_targets.extend(target.generate_phony_target())
            install_targets.extend(target.generate_install_target())
            uninstall_targets.extend(target.generate_uninstall_target())

        # Add a clean target.
        build_targets.add(MakefileTarget(name="clean", commands=f"rm -rf {self.build_dir}", phony=True, help=f"Removes the entire build directory."))

        # Add an install/uninstall target.
        install_targets.append(MakefileTarget(name="install", dependencies=[tgt.name for tgt in install_targets], phony=True, help=f"Runs all other install targets."))
        uninstall_targets.append(MakefileTarget(name="uninstall", dependencies=[tgt.name for tgt in uninstall_targets], phony=True, help=f"Runs all other uninstall targets."))

        # Create an all target as the first target, along with release and debug targets.
        phony_targets.insert(0, MakefileTarget(name="all", dependencies=["release", "debug"], phony=True, help=f"Builds all targets specified in this Makefile."))
        phony_targets.insert(1, MakefileTarget(name="release", dependencies=[tgt.path for tgt in self.release_targets], phony=True, help=f"Builds release targets specified in this Makefile."))
        phony_targets.insert(2, MakefileTarget(name="debug", dependencies=[tgt.path for tgt in self.debug_targets], phony=True, help=f"Builds debug targets specified in this Makefile."))

        all_targets = phony_targets + utils.convert_to_list(build_targets) + install_targets + uninstall_targets

        # Add a help target.
        help_target = MakefileTarget(name="help", phony=True, commands=[f'echo "\t{tgt.name}: {tgt.help}"' for tgt in all_targets if tgt.help])
        all_targets.append(help_target)

        # Create the final Makefile.
        target_sep = "\n\n"
        # Add verbosity options
        verbosity = f"ifdef VERBOSE\n\tAT=\nelse\n\tAT=@\nendif"
        Makefile = f"{MGen._get_makefile_header()}\n{verbosity}{utils.prefix_join(all_targets, target_sep)}"
        return Makefile

    def write(self, filename="Makefile", human_readable_object_names=False) -> None:
        makefile = self.generate(human_readable_object_names)
        # Assume the file is relative to the root directory.
        if not os.path.isabs(filename):
            filename = os.path.join(self.root_dir, filename)
        # Unlock file.
        with open(filename, "w") as outf:
            outf.write(makefile)
