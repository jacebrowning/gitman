"""Utilities to call shell programs."""

import os
import subprocess

import log

from . import common
from .exceptions import ShellError


CMD_PREFIX = "$ "
OUT_PREFIX = "> "


def call(name, *args, _show=True, _shell=False, _ignore=False):
    """Call a program with arguments.

    :param name: name of program to call
    :param args: list of command-line arguments
    :param _show: display the call on stdout
    :param _shell: force executing the program into a real shell
                   a Windows shell command (i.e: dir, echo) needs a real shell
                   but not a regular program (i.e: calc, git)
    :param _ignore: ignore non-zero return codes
    """
    program = show(name, *args, stdout=_show)

    command = subprocess.run(  # pylint: disable=subprocess-run-check
        name if _shell else [name, *args],
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=_shell,
    )

    output = [line.strip() for line in command.stdout.splitlines()]
    for line in output:
        log.debug(OUT_PREFIX + line)

    if command.returncode == 0:
        return output

    if _ignore:
        log.debug("Ignored error from call to '%s'", name)
        return output

    message = (
        "An external program call failed." + "\n\n"
        "In working directory: " + os.getcwd() + "\n\n"
        "The following command produced a non-zero return code:"
        + "\n\n"
        + CMD_PREFIX
        + program
        + "\n"
        + command.stdout.strip()
    )
    raise ShellError(message, program=program, output=output)


def mkdir(path):
    if not os.path.exists(path):
        if os.name == 'nt':
            call("mkdir " + path, _shell=True)
        else:
            call('mkdir', '-p', path)


def cd(path, _show=True):
    if os.name == 'nt':
        show('cd', '/D', path, stdout=_show)
    else:
        show('cd', path, stdout=_show)
    os.chdir(path)


def pwd(_show=True):
    cwd = os.getcwd()
    if os.name == 'nt':
        cwd = cwd.replace(os.sep, '/')
    show('cwd', cwd, stdout=_show)
    return cwd


def ln(source, target):
    dirpath = os.path.dirname(target)
    if not os.path.isdir(dirpath):
        mkdir(dirpath)
    os.symlink(source, target)


def rm(path):
    if os.name == 'nt':
        if os.path.isfile(path):
            call("del /Q /F " + path, _shell=True)
        elif os.path.isdir(path):
            call("rmdir /Q /S " + path, _shell=True)
    else:
        call('rm', '-rf', path)


def show(name, *args, stdout=True):
    program = ' '.join([name, *args])
    if stdout:
        common.show(CMD_PREFIX + program, color='shell')
    else:
        log.debug(CMD_PREFIX + program)
    return program
