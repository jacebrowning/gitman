"""Functions to manage the installation of dependencies."""

import os
import shutil

from . import common
from .config import load

log = common.logger(__name__)


def install(root=None, force=False, clean=True):
    """Install dependencies for a project."""
    log.info("%sinstalling dependencies...", 'force-' if force else '')

    root = _find_root(root)
    config = load(root)

    if config:
        count = config.install_deps(force=force, clean=clean, update=False)
    else:
        count = 0

    if count == 1:
        log.info("installed 1 dependency")
    elif count > 1:
        log.info("installed %s dependencies", count)
    else:
        log.warn("no dependencies installed")

    return count


def update(root=None, force=False, clean=True):
    """Update dependencies for a project."""
    log.info("%supdating dependencies...", 'force-' if force else '')

    root = _find_root(root)
    config = load(root)

    if config:
        count = config.install_deps(force=force, clean=clean)
    else:
        count = 0

    if count == 1:
        log.info("updated 1 dependency")
    elif count > 1:
        log.info("updated %s dependencies", count)
    else:
        log.warn("no dependencies updated")

    return count


def uninstall(root=None):
    """Uninstall dependencies for a project."""
    log.info("uninstalling dependencies...")

    root = _find_root(root)
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
    config = load(root)

    log.info("displaying dependencies...")
    if config:
        for path, url, sha in config.get_deps():
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
