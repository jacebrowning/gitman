"""Functions to manage the installation of dependencies."""

import os

from . import common
from .config import load

log = common.logger(__name__)


def install(root=None, force=False, clean=True):
    """Install dependencies for a project."""
    log.info("%sinstalling dependencies...", 'force-' if force else '')
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Installing dependencies...", log=False)
        common.show()
        count = config.install_deps(force=force, clean=clean, update=False)

    _display_result("install", "installed", count)

    return count


def update(root=None, force=False, clean=True):
    """Update dependencies for a project."""
    log.info("%supdating dependencies...", 'force-' if force else '')
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Updating dependencies...", log=False)
        common.show()
        count = config.install_deps(force=force, clean=clean)
        common.dedent(level=0)
        common.show("Recording installed versions...", log=False)
        common.show()
        config.lock_deps()

    _display_result("update", "updated", count)

    return count


def display(root=None, allow_dirty=True):
    """Display installed dependencies for a project."""
    log.info("displaying dependencies...")

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Displaying current dependency versions...", log=False)
        common.show()
        for path, url, revision in config.get_deps(allow_dirty=allow_dirty):
            log.info("revision: %s", revision)
            log.info("of repo: %s", url)
            log.info("at path: %s", path)
        log.info("all dependencies displayed")
    else:
        log.warn("no dependencies to display")

    return True


def delete(root=None, force=False):
    """Delete dependencies for a project."""
    log.info("deleting dependencies...")

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Checking for uncommitted changes...", log=False)
        common.show()
        for _ in config.get_deps(allow_dirty=force):
            pass
        common.dedent(level=0)
        common.show("Deleting all dependencies...", log=False)
        common.show()
        config.uninstall_deps()
        log.info("dependencies deleted")
        return True
    else:
        log.warn("no dependencies to delete")
        return False


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


def _display_result(present, past, count):
    if count is None:
        log.warn("no dependencies to %s", present)
    elif count == 1:
        log.info("%s 1 dependency", past)
    else:
        log.info("%s %s dependencies", past, count)
