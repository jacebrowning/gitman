"""Interface to the operating system."""

import os
import platform
import subprocess

import log


def launch(path):
    """Open a file with its default program."""
    name = platform.system()
    log.info("Opening %s", path)
    try:
        function = {
            'Windows': _launch_windows,
            'Darwin': _launch_mac,
            'Linux': _launch_linux,
        }[name]
    except KeyError:
        raise RuntimeError("Unrecognized platform: {}".format(name)) from None
    else:
        return function(path)


def _launch_windows(path):  # pragma: no cover (manual test)
    # pylint: disable=no-member
    os.startfile(path)  # type: ignore
    return True


def _launch_mac(path):  # pragma: no cover (manual test)
    return subprocess.call(['open', path]) == 0


def _launch_linux(path):  # pragma: no cover (manual test)
    return subprocess.call(['xdg-open', path]) == 0
