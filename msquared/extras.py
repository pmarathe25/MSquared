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
    # And is writable. If not, use root privilege.
    sudo = "sudo " if not os.access(install_dir, os.W_OK) else ""
    # Prefix with sudo if necessary and create the folder/files necessary.
    install_commands = [sudo + "mkdir -p " + install_dir, sudo + "touch " + install_file, sudo + 'printf \'#include "' + '"\\n#include "'.join(headers) + '"\' > ' + install_file]
    uninstall_commands = [sudo + "rm -rf " + install_file, sudo + "rmdir " + install_dir]
    mgen.add_custom_target(install_target, commands=install_commands, phony=True)
    mgen.add_custom_target(uninstall_target, commands=uninstall_commands, phony=True)
