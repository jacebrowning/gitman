"""Functions to manage the installation of dependencies."""

import os
import functools
import datetime
import logging

from . import common, system
from .models import load_config

log = logging.getLogger(__name__)


def restore_cwd(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        cwd = os.getcwd()
        result = func(*args, **kwargs)
        os.chdir(cwd)
        return result
    return wrapped


@restore_cwd
def install(*names, root=None, depth=None,
            force=False, fetch=False, clean=True):
    """Install dependencies for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `force`: indicates uncommitted changes can be overwritten
    - `fetch`: indicates the latest branches should always be fetched
    - `clean`: indicates untracked files should be deleted from dependencies

    """
    log.info("%sInstalling dependencies: %s",
             'force-' if force else '',
             ', '.join(names) if names else '<all>')
    count = None

    root = _find_root(root)
    config = load_config(root)

    if config:
        common.show("Installing dependencies...", log=False)
        common.show()
        count = config.install_deps(*names, update=False, depth=depth,
                                    force=force, fetch=fetch, clean=clean)

    return _display_result("install", "Installed", count)


@restore_cwd
def update(*names, root=None, depth=None,
           recurse=False, force=False, clean=True, lock=None):  # pylint: disable=redefined-outer-name
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
    config = load_config(root)

    if config:
        common.show("Updating dependencies...", log=False)
        common.show()
        count = config.install_deps(
            *names, update=True, depth=depth,
            recurse=recurse, force=force, fetch=True, clean=clean)
        common.dedent(level=0)
        if count and lock is not False:
            common.show("Recording installed versions...", log=False)
            common.show()
            config.lock_deps(*names, obey_existing=lock is None)

    return _display_result("update", "Updated", count)


@restore_cwd
def display(*, root=None, depth=None, allow_dirty=True):
    """Display installed dependencies for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `allow_dirty`: causes uncommitted changes to be ignored

    """
    log.info("Displaying dependencies...")
    count = None

    root = _find_root(root)
    config = load_config(root)

    if config:
        common.show("Displaying current dependency versions...", log=False)
        common.show()
        config.log(datetime.datetime.now().strftime("%F %T"))
        count = 0
        for identity in config.get_deps(depth=depth, allow_dirty=allow_dirty):
            count += 1
            config.log("{}: {} @ {}", *identity)
        config.log()

    return _display_result("display", "Displayed", count)


@restore_cwd
def lock(*names, root=None):
    """Lock current dependency versions for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree

    """
    log.info("Locking dependencies...")
    count = None

    root = _find_root(root)
    config = load_config(root)

    if config:
        common.show("Locking dependencies...", log=False)
        common.show()
        count = config.lock_deps(*names, obey_existing=False)
        common.dedent(level=0)

    return _display_result("lock", "Locked", count)


@restore_cwd
def delete(*, root=None, force=False):
    """Delete dependencies for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree
    - `force`: indicates uncommitted changes can be overwritten

    """
    log.info("Deleting dependencies...")
    count = None

    root = _find_root(root)
    config = load_config(root)

    if config:
        common.show("Checking for uncommitted changes...", log=False)
        common.show()
        count = len(list(config.get_deps(allow_dirty=force)))
        common.dedent(level=0)
        common.show("Deleting all dependencies...", log=False)
        common.show()
        config.uninstall_deps()

    return _display_result("delete", "Deleted", count, allow_zero=True)


def show(*names, root=None):
    """Display the path of an installed dependency or internal file.

    - `name`: dependency name or internal file keyword
    - `root`: specifies the path to the root working tree

    """
    log.info("Finding paths...")

    root = _find_root(root)
    config = load_config(root)
    if not config:
        log.error("No configuration found")
        return False

    for name in names or [None]:
        common.show(config.get_path(name))

    return True


def edit(*, root=None):
    """Open the confuration file for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree

    """
    log.info("Launching configuration...")

    root = _find_root(root)
    config = load_config(root)
    if not config:
        log.error("No configuration found")
        return False

    return system.launch(config.path)


def _find_root(base, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
        log.info("Current directory: %s", cwd)

    if base:
        root = os.path.abspath(base)
        log.info("Specified root: %s", root)

    else:
        log.info("Searching for root...")
        path = cwd
        prev = None
        root = None
        while path != prev:
            log.debug("Checking path: %s", path)
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
