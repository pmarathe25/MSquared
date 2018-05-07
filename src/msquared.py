

class MSquared(object):
    def __init__(self, build_dir="build/"):
        self.targets = []
        self.global_cflags = "-fPIC -c -march=native"
        self.global_lib_lflags = "-shared -march=native"
        self.global_exec_lflags = "-march=native"
        self.build_dir = build_dir
