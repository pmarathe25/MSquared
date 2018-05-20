from msquared._utils import _convert_to_list, _expand_glob_list
from msquared.MGen import MGen
from typing import List
import os

def add_installation(mgen, headers: List[str], install_file: str, install_target: str = "install", uninstall_target: str = "uninstall"):
    headers = _convert_to_list(headers)
    headers = _expand_glob_list(headers)
    # Make sure the install location exists.
    install_dir = os.path.dirname(install_file)
    install_file = os.path.abspath(install_file)
    temp_file = os.path.join(mgen.build_dir, os.path.basename(install_file))
    # And is writable. If not, use root privilege.
    sudo_install = "sudo " if not os.access(install_dir, os.W_OK) else ""
    sudo_temp = "sudo " if not os.access(mgen.build_dir, os.W_OK) else ""
    # Prefix with sudo if necessary and create the folder/files necessary.
    install_commands = [sudo_install + "mkdir -p " + install_dir, sudo_temp + 'printf \'#include "' + '"\\n#include "'.join(headers) + '"\\n\' > ' + temp_file, sudo_install + "mv " + temp_file + " " + install_file]
    uninstall_commands = [sudo_install + "rm -rf " + install_file, sudo_install + "rmdir " + install_dir]
    mgen.add_custom_target(install_target, commands=install_commands, phony=True)
    mgen.add_custom_target(uninstall_target, commands=uninstall_commands, phony=True)
