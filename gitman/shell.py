"""Utilities to call shell programs."""

import os
import subprocess
import logging

from . import common
from .exceptions import ShellError

CMD_PREFIX = "$ "
OUT_PREFIX = "> "

log = logging.getLogger(__name__)


def call(name, *args, _show=True, _ignore=False, _shell=False):
    """Call a program with arguments.

    :param name: name of program to call
    :param args: list of command-line arguments
    :param _show: display the call on stdout
    :param _ignore: ignore non-zero return codes
    :param _shell: force executing the program into a real shell
                   a Windows shell command (i.e: dir, echo) needs a real shell
                   but not a regular program (i.e: calc, git)
    """
    program = show(name, *args, stdout=_show)

    command = subprocess.run(
        [name, *args], universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        shell=_shell
    )

    for line in command.stdout.splitlines():
        log.debug(OUT_PREFIX + line.strip())

    if command.returncode == 0:
        return command.stdout.strip()

    elif _ignore:
        log.debug("Ignored error from call to '%s'", name)

    else:
        message = (
            "An external program call failed." + "\n\n"
            "In working directory: " + os.getcwd() + "\n\n"
            "The following command produced a non-zero return code:" + "\n\n" +
            program + "\n" +
            command.stdout
        )
        raise ShellError(message)


def mkdir(path):
    if not os.path.exists(path):
        if os.name == 'nt':
            call('mkdir', path, _shell=True)
        else:
            call('mkdir', '-p', path)


def cd(path, _show=True):
    if os.name == 'nt':
        # NOTE : call('cd', '/D', _shell=True) have no effect
        show('cd', '/D', path, stdout=_show)
    else:
        show('cd', path, stdout=_show)
    os.chdir(path)


def ln(source, target):
    if os.name == 'nt':
        log.warning("Symlinks are not supported on Windows")
    else:
        dirpath = os.path.dirname(target)
        if not os.path.isdir(dirpath):
            mkdir(dirpath)
        call('ln', '-s', source, target)


def rm(path):
    if os.path.exists(path):
        if os.name == 'nt':
            if os.path.isdir(path):
                call(
                    'rmdir', '/Q', '/S',
                    path, _shell=True
                )
            else:
                call('del', '/Q', '/F', path, _shell=True)
        else:
            call('rm', '-rf', path)


def show(name, *args, stdout=True):
    program = CMD_PREFIX + ' '.join([name, *args])
    if stdout:
        common.show(program, color='shell')
    else:
        log.debug(program)
    return program
