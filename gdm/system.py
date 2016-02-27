"""Interface to the operating system."""

import os
import platform
import subprocess
import logging

log = logging.getLogger(__name__)


def launch(path):  # pragma: no cover (manual test)
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
        raise AssertionError("Unknown OS: {}".format(name))
    else:
        return function(path)


def _launch_windows(path):  # pragma: no cover (manual test)
    os.startfile(path)  # pylint: disable=no-member
    return True


def _launch_mac(path):  # pragma: no cover (manual test)
    return subprocess.call(['open', path]) == 0


def _launch_linux(path):  # pragma: no cover (manual test)
    return subprocess.call(['xdg-open', path]) == 0
