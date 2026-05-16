import common_compiler_flags
from SCons.Tool import clang, clangxx
from SCons.Variables import BoolVariable


def options(opts):
    opts.Add(BoolVariable("use_llvm", "Use the LLVM compiler - only effective when targeting Linux", False))
    opts.Add(BoolVariable("use_static_cpp", "Link libgcc and libstdc++ statically for better portability", True))


def exists(env):
    return True


def configure(env):
    import subprocess

    def mySubProcess(cmdline, env):
        import shlex

        kwargs = {}
        args = shlex.split(cmdline)

        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=env,
            **kwargs,
        )
        data, err = proc.communicate()
        rv = proc.wait()
        if rv:
            print("=====")
            print(err.decode("utf-8"))
            print("=====")
        return rv

    def mySpawn(sh, escape, cmd, args, env):
        rv = 0
        if len(args) > 512 and cmd.endswith("ar"):
            cmdline = cmd + " " + args[1] + " " + args[2] + " "
            for i in range(3, len(args), 510):
                batch = args[i : i + 510]
                line = cmdline + " ".join(batch)
                print(line)
                rv = mySubProcess(line, env)
                if rv:
                    break
        else:
            newargs = " ".join(args[1:])
            cmdline = cmd + " " + newargs
            if cmd.endswith("ar"):
                print(cmdline)
            rv = mySubProcess(cmdline, env)

        return rv

    env["SPAWN"] = mySpawn
    env.Replace(ARFLAGS=["q"])


def generate(env):
    if env["use_llvm"]:
        clang.generate(env)
        clangxx.generate(env)
    elif env.use_hot_reload:
        # Required for extensions to truly unload.
        env.Append(CXXFLAGS=["-fno-gnu-unique"])

    env.Append(CCFLAGS=["-fPIC", "-Wwrite-strings"])
    env.Append(LINKFLAGS=["-Wl,-R,'$$ORIGIN'"])

    if env["arch"] == "x86_64":
        # -m64 and -m32 are x86-specific already, but it doesn't hurt to
        # be clear and also specify -march=x86-64. Similar with 32-bit.
        env.Append(CCFLAGS=["-m64", "-march=x86-64"])
        env.Append(LINKFLAGS=["-m64", "-march=x86-64"])
    elif env["arch"] == "x86_32":
        env.Append(CCFLAGS=["-m32", "-march=i686"])
        env.Append(LINKFLAGS=["-m32", "-march=i686"])
    elif env["arch"] == "arm64":
        env.Append(CCFLAGS=["-march=armv8-a"])
        env.Append(LINKFLAGS=["-march=armv8-a"])
    elif env["arch"] == "rv64":
        env.Append(CCFLAGS=["-march=rv64gc"])
        env.Append(LINKFLAGS=["-march=rv64gc"])

    # Link statically for portability
    if env["use_static_cpp"]:
        env.Append(LINKFLAGS=["-static-libgcc", "-static-libstdc++"])

    env.Append(CPPDEFINES=["LINUX_ENABLED", "UNIX_ENABLED"])

    # Refer to https://github.com/godotengine/godot/blob/master/platform/linuxbsd/detect.py
    if env["lto"] == "auto":
        env["lto"] = "full"

    common_compiler_flags.generate(env)

    configure(env)
