from typing import List, Set, Dict
from msquared import utils
from msquared.Logger import Logger
import sys
import os

# Represents a target in a makefile. This consists of a name, dependencies, and commands.
class MakefileTarget(object):
    def __init__(self, name: str, dependencies = set(), commands = [], phony = False, help=""):
        self.name = name
        self.dependencies = utils.convert_to_set(dependencies)
        self.commands = utils.convert_to_list(commands)
        self.phony = phony
        self.help = help

    def __str__(self):
        cmd_sep = "\n\t$(AT)"
        phony_line = f".PHONY: {self.name}"
        target_line = f"{self.name}:{utils.prefix_join(self.dependencies)}{utils.prefix_join(self.commands, cmd_sep)}"
        return f"{phony_line}\n{target_line}" if self.phony else f"{target_line}"

    def __repr__(self):
        return self.__str__()

    # Equality is based solely on the target name, since we cannot have duplicate names in the Makefile.
    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

# A Target represents a linked target, like a library or executable.
# It has cflags and include_dirs, which are propagated to constituent objects
# (based on deps), as well as lflags and link_dirs which it uses.
# TODO: Change shell commands to the same way compilers are done.
class Target(object):
    def __init__(self, name: str, path: str, source_map=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), compiler="", logger=Logger(), obj_out_dir="", install_dir=""):
        """
        Represents an executable or library.

        Args:
            name (str): The name of the executable or library.

        Optional Args:
            source_map (Dict[str]): The constituent .cpp files mapped to their header dependencies.
            libraries (Set[str]): Libraries that should be linked against this target.
            cflags (Set[str]): Compiler flags for this target.
            include_dirs (Set[str]): Include directories for this target.
            lflags (Set[str]): Linker flags for this target.
            link_dirs (Set[str]): Link directories for this target.
            compiler (BaseCompiler): The compiler to use.
            out_dir (str): The output directory for the final build artifact.
            logger (Logger): The logger to use.
            obj_out_dir (str): The output directory for intermediate build artifacts.
            install_dir (str): The directory to install the final build artifact to.
        """
        self.path = path
        self.set_name(name)
        self.obj_out_dir = obj_out_dir
        self.source_map = source_map
        self.libraries = libraries
        self.cflags = cflags
        self.include_dirs = include_dirs
        self.lflags = lflags
        self.link_dirs = link_dirs
        self.compiler = compiler
        self.logger = logger
        self.install_dir = ""
        if install_dir and not os.path.isabs(install_dir):
            self.logger.warning(f"Install dir {install_dir} is not an absolute path. Will not install.")
        else:
            self.install_dir = install_dir

    def set_name(self, name: str) -> None:
        self.name = name
        self.clean_name = f"clean_{self.name}"
        self.install_name = f"install_{self.name}"
        self.uninstall_name = f"uninstall_{self.name}"

    def add_flags(self, flags: Set[str]) -> None:
        self.cflags |= utils.convert_to_set(flags)
        self.lflags |= utils.convert_to_set(flags)

    # Generate a MakefileTarget for a source file.
    def generate_object_target(self, source: str, human_readable_object_names=False) -> MakefileTarget:
        # Generates an object name for this source file.
        def generate_object_path(source):
            # Prepare the target. We name object files based on compiler + cflags.
            # The assumption is that if these are the same between two objects, they are equivalent.
            # Some of the flags need to be sanitized first though.
            san_cflags = [self.compiler.name] + [flag.replace("=", "eq") for flag in self.cflags] + utils.convert_to_list(self.include_dirs)
            uid = f"{hash(tuple(san_cflags)) % ((sys.maxsize + 1) * 2)}"
            if human_readable_object_names:
                uid = f"{''.join(san_cflags)}"
            filename = f"{os.path.basename(os.path.splitext(source)[0])}.{uid}.o"
            self.logger.debug(f"For {source}, using filename: {filename} and directory: {self.obj_out_dir}")
            return os.path.join(self.obj_out_dir, filename)

        object_path = generate_object_path(source)
        commands = []
        # Make sure the directory exists when building the target.
        commands.append(f"mkdir -p {os.path.dirname(object_path)}")
        # Add compilation command.
        commands.append(f'echo -e "\\e[32mCompiling {object_path}\\e[0m"')
        commands.append(f"{self.compiler.name} {source} -o {object_path}{utils.prefix_join(self.include_dirs, ' -I')} {' '.join(self.cflags)} {self.compiler.compile_only}")
        return MakefileTarget(name=object_path, dependencies=set([source]) | self.source_map[source], commands=commands)

    # TODO: Docstrings.
    def generate_build_targets(self, library_registry: Dict[str, str], human_readable_object_names=False) -> List[MakefileTarget]:
        if not self.source_map or not self.compiler:
            return []
        # First, generate all object targets.
        makefile_targets = []
        for source in self.source_map.keys():
            self.logger.debug(f"Generating object target for {source}")
            obj_target = self.generate_object_target(source, human_readable_object_names)
            makefile_targets.append(obj_target)

        objects = set([obj.name for obj in makefile_targets])
        # Distinguish between libraries created internal to the project vs external dependencies.
        internal_libraries = set()
        external_libraries = set()
        for lib in self.libraries:
            if lib in library_registry:
                internal_libraries.add(library_registry[lib])
            else:
                external_libraries.add(utils.prefix("-l", lib) if not utils.hasext(lib) else lib)

        commands = []
        commands.append(f'echo -e "\\e[92m\\e[1mLinking {self.path}\\e[0m"')
        commands.append(f"{self.compiler.name} {' '.join(objects)} -o {self.path}{utils.prefix_join(self.link_dirs, ' -L')} {' '.join(internal_libraries | external_libraries)} {' '.join(self.lflags)}")
        # Finally, generate a target for the final linked executable/library.
        makefile_targets.append(MakefileTarget(name=self.path, dependencies=(objects | internal_libraries), commands=commands))
        # Add a clean target.
        makefile_targets.append(MakefileTarget(name=self.clean_name, commands=f"rm -rf {self.path} {' '.join(objects)}", phony=True, help=f"Removes {self.name} and its constituent object files."))
        return makefile_targets

    def generate_phony_target(self) -> List[MakefileTarget]:
        if self.name == self.path or not self.source_map or not self.compiler:
            return []
        # Generate a phony target as a shorthand representation for this target.
        return utils.convert_to_list(MakefileTarget(name=self.name, dependencies=self.path, phony=True, help=f"Builds {self.name}"))

    def generate_install_target(self) -> List[MakefileTarget]:
        if not self.install_dir:
            return []
        # Check if we need root permissions for this directory.
        sudo = "sudo " if utils.requires_root(self.install_dir) else ""
        commands = []
        commands.append(f'echo -e "\\e[34m\\e[1mInstalling {self.path} to {self.install_dir}\\e[0m"')
        commands.append(f"{sudo}mkdir -p {self.install_dir}")
        commands.append(f"{sudo}cp -r {self.path} {self.install_dir}")
        return utils.convert_to_list(MakefileTarget(name=self.install_name, dependencies=self.path, phony=True, commands=commands, help=f"Installs {self.path} to {self.install_dir}."))

    def generate_uninstall_target(self) -> List[MakefileTarget]:
        if not self.install_dir:
            return []
        # Check if we need root permissions for the install directory.
        sudo = "sudo " if utils.requires_root(self.install_dir) else ""
        commands = []
        filename = os.path.basename(self.path)
        commands.append(f'echo -e "\\e[31m\\e[1mUninstalling {os.path.join(self.install_dir, filename)}\\e[0m"')
        commands.append(f"{sudo}rm -rf {os.path.join(self.install_dir, filename)}")
        commands.append(f"{sudo}rmdir --ignore-fail-on-non-empty {self.install_dir}")
        return utils.convert_to_list(MakefileTarget(name=self.uninstall_name, phony=True, commands=commands, help=f"Removes {os.path.join(self.install_dir, filename)} and then removes the directory if it is empty."))
