"""Utilities to call shell programs."""

import os
import subprocess
import logging

from . import common
from .exceptions import ShellError

CMD_PREFIX = "$ "
OUT_PREFIX = "> "

log = logging.getLogger(__name__)


def call(program, *args, _show=True, _ignore=False):
    """Call a shell program with arguments."""
    msg = CMD_PREFIX + ' '.join([program, *args])
    if _show:
        common.show(msg)
    else:
        log.debug(msg)

    if program == 'cd':
        assert len(args) == 1, "'cd' takes a single argument"
        return os.chdir(args[0])

    command = subprocess.run([program, *args], universal_newlines=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in command.stdout.splitlines():
        log.debug(OUT_PREFIX + line.strip())

    if command.returncode == 0:
        return command.stdout.strip()

    elif _ignore:
        log.debug("Ignored error from call to '%s'", program)

    else:
        raise ShellError("TODO: create an error message similar to 'sh'")


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
