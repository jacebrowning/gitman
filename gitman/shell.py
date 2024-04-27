"""Utilities to call shell programs."""

import os
import subprocess

import log

from . import common
from .exceptions import ShellError

CMD_PREFIX = "$ "
OUT_PREFIX = "> "


def call(name, *args, _show=True, _stream=True, _shell=False, _ignore=False):
    """Call a program with arguments.

    :param name: name of program to call
    :param args: list of command-line arguments
    :param _show: display the call arguments
    :param _stream: stream realtime output of the call
    :param _shell: force executing the program into a real shell
                   a Windows shell command (i.e: dir, echo) needs a real shell
                   but not a regular program (i.e: calc, git)
    :param _ignore: ignore non-zero return codes
    """
    if not _show:
        _stream = False

    program = show(name, *args, stdout=_show)

    # PyInstaller saves the original value to *_ORIG, then modifies the search
    # path so that the bundled libraries are found first by the bundled code.
    # But if your code executes a system program, you often do not want that
    # this system program loads your bundled libraries (that are maybe not
    # compatible with your system program) - it rather should load the correct
    # libraries from the system locations like it usually does.
    # Thus you need to restore the original path before creating the subprocess
    # with the system program
    # https://github.com/pyinstaller/pyinstaller/blob/483c819d6a256b58db6740696a901bd41c313f0c/doc/runtime-information.rst#ld_library_path--libpath-considerations
    env = dict(os.environ)  # make a copy of the environment
    lp_key = "LD_LIBRARY_PATH"  # for Linux and *BSD.
    lp_orig = env.get(lp_key + "_ORIG")  # pyinstaller >= 20160820 has this
    if lp_orig is not None:
        env[lp_key] = lp_orig  # restore the original, unmodified value
    else:
        env.pop(lp_key, None)  # last resort: remove the env var

    command = (
        subprocess.Popen(  # pylint: disable=subprocess-run-check,consider-using-with
            name if _shell else [name, *args],
            encoding="utf-8",
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=_shell,
            env=env,
        )
    )

    # Poll process.stdout to show stdout live
    complete_output = []
    while True:
        assert command.stdout
        output = command.stdout.readline()
        if output == "" and command.poll() is not None:
            break

        if output != "":
            output = output.strip()
        else:
            continue

        complete_output.append(output)
        if _stream:
            common.show(output, color="shell_output")
        else:
            log.debug(OUT_PREFIX + output)

    if command.returncode == 0:
        return complete_output

    if _ignore:
        log.debug("Ignored error from call to '%s'", name)
        return complete_output

    message = (
        "An external program call failed." + "\n\n"
        "In working directory: " + os.getcwd() + "\n\n"
        "The following command produced a non-zero return code:"
        + "\n\n"
        + CMD_PREFIX
        + program
        + "\n".join(complete_output)
    )
    raise ShellError(message, program=program, output=complete_output)


def mkdir(path):
    if not os.path.exists(path):
        if os.name == "nt":
            call("mkdir " + path, _shell=True)
        else:
            call("mkdir", "-p", path)


def cd(path, _show=True):
    if os.name == "nt":
        show("cd", "/D", path, stdout=_show)
    else:
        show("cd", path, stdout=_show)
    os.chdir(path)


def pwd(_show=True):
    cwd = os.getcwd()
    if os.name == "nt":
        cwd = cwd.replace(os.sep, "/")
    show("cwd", cwd, stdout=_show)
    return cwd


def ln(source, target):
    dirpath = os.path.dirname(target)
    if not os.path.isdir(dirpath):
        mkdir(dirpath)
    os.symlink(source, target)


def rm(path):
    if os.name == "nt":
        if os.path.isfile(path):
            call("del /Q /F " + path, _shell=True)
        elif os.path.isdir(path):
            call("rmdir /Q /S " + path, _shell=True)
    else:
        call("rm", "-rf", path)


def show(name, *args, stdout=True):
    program = " ".join([name, *args])
    if stdout:
        common.show(CMD_PREFIX + program, color="shell")
    else:
        log.debug(CMD_PREFIX + program)
    return program
