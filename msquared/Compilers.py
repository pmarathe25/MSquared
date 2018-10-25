class BaseCompiler(object):
    def __init__(self, name, compile_only, shared, debug, default_flags=set()):
        self.name = name
        self.compile_only = compile_only
        self.shared = shared
        self.debug = debug
        self.default_flags = default_flags

GCC = BaseCompiler("g++", "-c", "-shared -fPIC", "-g", default_flags=set(["--std=c++17", "-O3", "-flto", "-march=native"]))
