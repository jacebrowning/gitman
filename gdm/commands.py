"""Functions to manage the installation of dependencies."""

import os
import shutil

from . import common
from .config import load, install_deps, get_deps

log = common.logger(__name__)


def install(root=None, force=False):
    """Install dependencies for a project."""
    root = _find_root(root)

    log.info("%sinstalling dependencies...", 'force-' if force else '')
    count = install_deps(root, force=force)
    if count == 1:
        log.info("installed 1 dependency")
    elif count > 1:
        log.info("installed %s dependencies", count)
    else:
        log.warn("no dependencies installed")

    return count


def uninstall(root=None):
    """Uninstall dependencies for a project."""
    root = _find_root(root)

    log.info("uninstalling dependencies...")
    config = load(root)
    if config:
        if os.path.exists(config.location):
            log.debug("deleting '%s'...", config.location)
            shutil.rmtree(config.location)
        log.info("dependencies uninstalled")
        return True
    else:
        log.warn("no dependencies to uninstall")
        return False


def display(root=None):
    """Display installed dependencies for a project."""
    root = _find_root(root)

    log.info("displaying dependencies...")
    for path, url, sha in get_deps(root):
        common.show("{p}: {u} @ {s}".format(p=path, u=url, s=sha))
    log.info("all dependencies displayed")

    return True


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
