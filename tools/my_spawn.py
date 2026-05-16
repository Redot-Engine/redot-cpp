import os


def exists(env):
    return os.name == "nt"


# Workaround for MinGW. See:
# http://www.scons.org/wiki/LongCmdLinesOnWin32
def configure(env):
    import subprocess

    def mySubProcess(cmdline, env):
        # print "SPAWNED : " + cmdline
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            cmdline,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo,
            shell=False,
            env=env,
        )
        rv = proc.wait()
        return rv

    def mySpawn(sh, escape, cmd, args, env):
        newargs = " ".join(args[1:])
        cmdline = cmd + " " + newargs

        rv = 0
        if len(cmdline) > 32000 and cmd.endswith("ar"):
            cmdline_base = cmd + " " + args[1] + " " + args[2] + " "

            i = 3
            while i < len(args):
                batch_args = []
                current_len = len(cmdline_base)

                while i < len(args) and current_len + len(args[i]) + 1 < 32000:
                    batch_args.append(args[i])
                    current_len += len(args[i]) + 1
                    i += 1

                if not batch_args:  # Should not happen unless a single arg is > 32000
                    batch_args.append(args[i])
                    i += 1

                rv = mySubProcess(cmdline_base + " ".join(batch_args), env)
                if rv:
                    break
        else:
            rv = mySubProcess(cmdline, env)

        return rv

    env["SPAWN"] = mySpawn
    env.Replace(ARFLAGS=["q"])
