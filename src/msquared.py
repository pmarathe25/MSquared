from _utils import _handle_str

class MSquared(object):
    def __init__(self, build_dir="build/"):
        # Dictionary of {target_name: target_contents}
        self.targets = {}
        self.global_cflags = "-fPIC -c -march=native"
        self.global_lib_lflags = "-shared -march=native"
        self.global_exec_lflags = "-march=native"
        self.build_dir = build_dir

    def __getitem__(self, index):
        return self.targets[index]

    """ Functions for generating targets_contents. """

    def add_clean(files=[]):
        files = _handle_str(files)
