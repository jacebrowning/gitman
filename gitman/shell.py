"""Utilities to call shell programs."""

import os
import subprocess
import logging

from . import common
from .exceptions import ShellError

CMD_PREFIX = "$ "
OUT_PREFIX = "> "

log = logging.getLogger(__name__)


def call(name, *args, _show=True, _ignore=False):
    """Call a shell program with arguments.

    :param name: name of program to call
    :param args: list of command-line arguments
    :param _show: display the call on stdout
    :param _ignore: ignore non-zero return codes

    """
    program = CMD_PREFIX + ' '.join([name, *args])
    if _show:
        common.show(program)
    else:
        log.debug(program)

    if name == 'cd':
        return os.chdir(args[0])  # 'cd' has no effect in a subprocess

    command = subprocess.run(
        [name, *args], universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    for line in command.stdout.splitlines():
        log.debug(OUT_PREFIX + line.strip())

    if command.returncode == 0:
        return command.stdout.strip()

    elif _ignore:
        log.debug("Ignored error from call to '%s'", program)

    else:
        message = (
            "An external program call failed." + "\n\n"
            "In worikng directory: " + os.getcwd() + "\n\n"
            "The following command produced a non-zero return code:" + "\n\n" +
            program + "\n" +
            command.stdout
        )
        raise ShellError(message)


def mkdir(path):
    call('mkdir', '-p', path)


def cd(path, _show=True):
    call('cd', path, _show=_show)


def ln(source, target):
    dirpath = os.path.dirname(target)
    if not os.path.isdir(dirpath):
        mkdir(dirpath)
    call('ln', '-s', source, target)


def rm(path):
    call('rm', '-rf', path)
