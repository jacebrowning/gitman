"""Functions to manage the installation of dependencies."""

import os

from . import common
from . import config

log = common.logger(__name__)


def install(root=None):
    """Install dependencies for a project."""
    root = _find_root(root)

    log.info("installing dependencies...")
    count = config.install_deps(root)
    if count == 1:
        log.info("installed 1 dependency")
    elif count > 1:
        log.info("installed %s dependencies", count)
    else:
        log.warn("no dependencies installed")

    return count


def _find_root(root, cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    if root:
        root = os.path.abspath(root)
        log.info("specified root: %s", root)
    else:
        path = cwd
        prev = None

        log.info("searching for root...")
        while path != prev:
            log.debug("path: %s", path)
            if '.git' in os.listdir(path):
                root = path
                break
            prev = path
            path = os.path.dirname(path)

        if root:
            log.info("found root: %s", root)
        else:
            root = cwd
            log.warning("no root found, default: %s", root)

    return root
