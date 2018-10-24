from typing import List, Set
from msquared import utils
from msquared.Logger import Logger
import os

# A Target represents a linked target, like a library or executable.
# It has cflags and include_dirs, which are propagated to constituent objects
# (based on deps), as well as lflags and link_dirs which it uses.
class Target(object):
    def __init__(self, name: str, source_map=set(), libraries=set(), cflags=set(), include_dirs=set(), lflags=set(), link_dirs=set(), compiler="", out_dir="", logger=Logger()):
        # TODO: Update docstring.
        """
        Represents an executable or library.

        Args:
            name (str): The name of the executable or library.
            source_map (Dict[str]): The constituent .cpp files mapped to their header dependencies.
            libraries (Set[str]): Libraries that should be linked against this target.
            cflags (Set[str]): Compiler flags for this target.
            include_dirs (Set[str]): Include directories for this target.
            lflags (Set[str]): Linker flags for this target.
            link_dirs (Set[str]): Link directories for this target.
        """
        self.target_out_dir = out_dir
        self.update_name(name)
        self.update_obj_subdir("objs")
        self.source_map = source_map
        self.objects = set()
        self.deps = set()
        self.libraries = libraries
        self.cflags = cflags
        self.include_dirs = include_dirs
        self.lflags = lflags
        self.link_dirs = link_dirs
        self.compiler = compiler
        self.logger = logger

    def update_name(self, name):
        self.name = name
        self.path = os.path.join(self.target_out_dir, name)
        self.clean_name = f"clean_{self.name}"

    def update_obj_subdir(self, subdir):
        self.obj_out_dir = os.path.join(self.target_out_dir, subdir)

    def add_flags(self, flags):
        self.cflags |= utils.convert_to_set(flags)
        self.lflags |= utils.convert_to_set(flags)

    # Generate a MakefileTarget for a source file.
    def generate_object_target(self, source):
        # Generates an object name for this source file.
        def generate_object_name(source):
            # Prepare the target. We name object files based on compiler + cflags.
            # The assumption is that if these are the same between two objects, they are equivalent.
            # Some of the flags need to be sanitized first though.
            san_cflags = [flag.replace("=", "eq") for flag in self.cflags]
            uid = f"{self.compiler.name}{''.join(san_cflags)}"
            filename = f"{os.path.basename(os.path.splitext(source)[0])}.{uid}.o"
            self.logger.debug(f"For {source}, using filename: {filename} and directory: {self.obj_out_dir}")
            return os.path.join(self.obj_out_dir, filename)

        path = generate_object_name(source)
        # Add to this target's dependencies.
        self.objects.add(path)
        self.deps.add(path)
        commands = []
        # Make sure the directory exists when building the target.
        commands.append(f"mkdir -p {os.path.dirname(path)}")
        # Add compilation command.
        commands.append(f'echo -e "\\e[32mCompiling {source}"')
        commands.append(f"{self.compiler.name} {source} -o {path}{utils.prefix_join(self.include_dirs, ' -I')} {' '.join(self.cflags)} {self.compiler.compile_only}")
        return MakefileTarget(name=path, dependencies=self.source_map[source], commands=commands)

    def generate_makefile_targets(self):
        # TODO: Docstring.

        # First, generate all object targets.
        makefile_targets = []
        for source in self.source_map.keys():
            self.logger.debug(f"Generating object target for {source}")
            makefile_targets.append(self.generate_object_target(source))

        commands = []
        commands.append(f'echo -e "\\e[92m\\e[1mLinking {self.name}"')
        commands.append(f"{self.compiler.name} {' '.join(self.objects)} -o {self.path}{utils.prefix_join(self.link_dirs, ' -L')} {' '.join(self.libraries)} {' '.join(self.lflags)}")
        # Generate a phony target as a shorthand representation for this target.
        makefile_targets.append(MakefileTarget(name=self.name, dependencies=self.path, phony=True, help=f"Builds {self.name}"))
        # Finally, generate a target for the final linked executable/library.
        makefile_targets.append(MakefileTarget(name=self.path, dependencies=self.deps, commands=commands))
        # Add a clean target.
        makefile_targets.append(MakefileTarget(name=self.clean_name, commands=f"rm -rf {self.path} {' '.join(self.objects)}", phony=True, help=f"Removes {self.name} and its constituent object files."))
        return makefile_targets

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
