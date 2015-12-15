"""Functions to manage the installation of dependencies."""

import os
import logging

from . import common
from .config import load

log = logging.getLogger(__name__)


def install(*names, root=None, depth=None, force=False, clean=True):
    """Install dependencies for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `force`: indicates uncommitted changes can be overwritten
    - `clean`: indicates untracked files should be deleted from dependencies

    """
    log.info("%sInstalling dependencies: %s",
             'force-' if force else '',
             ', '.join(names) if names else '<all>')
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Installing dependencies...", log=False)
        common.show()
        count = config.install_deps(
            *names, update=False, depth=depth, force=force, clean=clean)

    return _display_result("install", "Installed", count)


def update(*names, root=None, depth=None,
           recurse=False, force=False, clean=True, lock=True):
    """Update dependencies for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `recurse`: indicates nested dependencies should also be updated
    - `force`: indicates uncommitted changes can be overwritten
    - `clean`: indicates untracked files should be deleted from dependencies
    - `lock`: indicates actual dependency versions should be recorded

    """
    log.info("%s dependencies%s: %s",
             'Force updating' if force else 'Updating',
             ', recursively' if recurse else '',
             ', '.join(names) if names else '<all>')
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Updating dependencies...", log=False)
        common.show()
        count = config.install_deps(
            *names, update=True, depth=depth,
            recurse=recurse, force=force, clean=clean)
        common.dedent(level=0)
        if count and lock:
            common.show("Recording installed versions...", log=False)
            common.show()
            config.lock_deps(*names)

    return _display_result("update", "Updated", count)


def display(root=None, depth=None, allow_dirty=True):
    """Display installed dependencies for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `allow_dirty`: causes uncommitted changes to be ignored

    """
    log.info("Displaying dependencies...")
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Displaying current dependency versions...", log=False)
        common.show()
        count = len(list(config.get_deps(depth=depth, allow_dirty=allow_dirty)))

    return _display_result("display", "Displayed", count)


def delete(root=None, force=False):
    """Delete dependencies for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree
    - `force`: indicates uncommitted changes can be overwritten

    """
    log.info("Deleting dependencies...")
    count = None

    root = _find_root(root)
    config = load(root)

    if config:
        common.show("Checking for uncommitted changes...", log=False)
        common.show()
        count = len(list(config.get_deps(allow_dirty=force)))
        common.dedent(level=0)
        common.show("Deleting all dependencies...", log=False)
        common.show()
        config.uninstall_deps()

    return _display_result("delete", "Deleted", count, allow_zero=True)


def _find_root(root, cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    if root:
        root = os.path.abspath(root)
        log.info("Specified root: %s", root)
    else:
        path = cwd
        prev = None

        log.info("Searching for root...")
        while path != prev:
            log.debug("Path: %s", path)
            if '.git' in os.listdir(path):
                root = path
                break
            prev = path
            path = os.path.dirname(path)

        if root:
            log.info("Found root: %s", root)
        else:
            root = cwd
            log.warning("No root found, default: %s", root)

    return root


def _display_result(present, past, count, allow_zero=False):
    """Convert a command's dependency count to a return status.

    >>> _display_result("sample", "Sampled", 1)
    True

    >>> _display_result("sample", "Sampled", None)
    False

    >>> _display_result("sample", "Sampled", 0)
    False

    >>> _display_result("sample", "Sampled", 0, allow_zero=True)
    True

    """
    if count is None:
        log.warning("No dependencies to %s", present)
    elif count == 1:
        log.info("%s 1 dependency", past)
    else:
        log.info("%s %s dependencies", past, count)

    if count:
        return True
    elif count is None:
        return False
    else:
        assert count == 0
        return allow_zero
