# from msquared import utils as utils
# from msquared.MGen import MGen
# from typing import List
# import os
#
# def add_installation(mgen, headers: List[str], install_file: str, install_target: str = "install", uninstall_target: str = "uninstall"):
#     deps = utils._expand_glob_list(utils._convert_to_iterable(headers))
#     headers = MGen.StringList([os.path.abspath(header) for header in deps], prefix="#include \"", suffix="\"\\n")
#     # Make sure the install location exists.
#     install_dir = os.path.dirname(install_file)
#     install_file = os.path.abspath(install_file)
#     temp_file = os.path.join(mgen.build_root, install_target + "_" + os.path.basename(install_file))
#     # And is writable. If not, use root privilege.
#     sudo_install = "sudo " if not os.access(install_dir, os.W_OK) else ""
#     sudo_temp = "sudo " if not os.access(mgen.build_root, os.W_OK) else ""
#     # Prefix with sudo if necessary and create the folder/files necessary.
#     install_commands = [f"{sudo_install}mkdir -p {install_dir}", f"{sudo_temp}printf '{headers}' > {temp_file}", f"{sudo_install}mv {temp_file} {install_file}"]
#     uninstall_commands = [f"{sudo_install}rm -rf {install_file}", f"-{sudo_install} rmdir {install_dir} --ignore-fail-on-non-empty"]
#     mgen.add_target(install_file, deps=deps, cmds=install_commands, alias=install_target, clean=False)
#     mgen.add_target(uninstall_target, cmds=uninstall_commands, clean=False, phony=True)
