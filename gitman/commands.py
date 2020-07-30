"""Functions to manage the installation of dependencies."""

import datetime
import functools
import os

import log

from . import common, system
from .models import Config, Source, load_config


def restore_cwd(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        cwd = os.getcwd()
        result = func(*args, **kwargs)
        os.chdir(cwd)
        return result

    return wrapped


def init():
    """Create a new config file for the project."""
    success = False

    config = load_config()

    if config:
        msg = "Configuration file already exists: {}".format(config.path)
        common.show(msg, color='error')

    else:
        config = Config()
        source = Source(
            type='git',
            name="sample_dependency",
            repo="https://github.com/githubtraining/hellogitworld",
        )
        config.sources.append(source)
        source = source.lock(rev="ebbbf773431ba07510251bb03f9525c7bab2b13a")
        config.sources_locked.append(source)
        config.datafile.save()

        msg = "Created sample config file: {}".format(config.path)
        common.show(msg, color='success')
        success = True

    msg = "To edit this config file, run: gitman edit"
    common.show(msg, color='message')

    return success


@restore_cwd
def install(
    *names,
    root=None,
    depth=None,
    force=False,
    fetch=False,
    force_interactive=False,
    clean=True,
    skip_changes=False,
):
    """Install dependencies for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `force`: indicates uncommitted changes can be overwritten and
               script errors can be ignored
    - `force_interactive`: indicates uncommitted changes can be interactively
    overwritten and script errors can be ignored
    - `fetch`: indicates the latest branches should always be fetched
    - `clean`: indicates untracked files should be deleted from dependencies
    - `skip_changes`: indicates dependencies with uncommitted changes
     should be skipped
    """
    log.info(
        "%sInstalling dependencies: %s",
        'force-' if force or force_interactive else '',
        ', '.join(names) if names else '<all>',
    )
    count = None

    config = load_config(root)

    if config:
        common.newline()
        common.show("Installing dependencies...", color='message', log=False)
        common.newline()
        count = config.install_dependencies(
            *names,
            update=False,
            depth=depth,
            force=force,
            force_interactive=force_interactive,
            fetch=fetch,
            clean=clean,
            skip_changes=skip_changes,
        )

        if count:
            _run_scripts(
                *names, depth=depth, force=force, _config=config, show_shell_stdout=True
            )

    return _display_result("install", "Installed", count)


@restore_cwd
def update(
    *names,
    root=None,
    depth=None,
    recurse=False,
    force=False,
    force_interactive=False,
    clean=True,
    lock=None,  # pylint: disable=redefined-outer-name
    skip_changes=False,
):
    """Update dependencies for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `root`: specifies the path to the root working tree
    - `depth`: number of levels of dependencies to traverse
    - `recurse`: indicates nested dependencies should also be updated
    - `force`: indicates uncommitted changes can be overwritten and
               script errors can be ignored
    - `force_interactive`: indicates uncommitted changes can be interactively
    overwritten and script errors can be ignored
    - `clean`: indicates untracked files should be deleted from dependencies
    - `lock`: indicates updated dependency versions should be recorded
    - `skip_changes`: indicates dependencies with uncommitted changes
     should be skipped
    """
    log.info(
        "%s dependencies%s: %s",
        'Force updating' if force or force_interactive else 'Updating',
        ', recursively' if recurse else '',
        ', '.join(names) if names else '<all>',
    )
    count = None

    config = load_config(root)

    if config:
        common.newline()
        common.show("Updating dependencies...", color='message', log=False)
        common.newline()
        count = config.install_dependencies(
            *names,
            update=True,
            depth=depth,
            recurse=recurse,
            force=force,
            force_interactive=force_interactive,
            fetch=True,
            clean=clean,
            skip_changes=skip_changes,
        )

        if count and lock is not False:
            common.show("Recording installed versions...", color='message', log=False)
            common.newline()
            config.lock_dependencies(
                *names,
                obey_existing=lock is None,
                skip_changes=skip_changes or force_interactive,
            )

        if count:
            _run_scripts(
                *names, depth=depth, force=force, _config=config, show_shell_stdout=True
            )

    return _display_result("update", "Updated", count)


def _run_scripts(
    *names, depth=None, force=False, _config=None, show_shell_stdout=False
):
    """Run post-install scripts.

    Optional arguments:

    - `*names`: optional list of dependency directory names filter on
    - `depth`: number of levels of dependencies to traverse
    - `force`: indicates script errors can be ignored
    - `show_shell_stdout`: allows to print realtime output from shell commands

    """
    assert _config, "'_config' is required"

    common.show("Running scripts...", color='message', log=False)
    common.newline()
    _config.run_scripts(
        *names, depth=depth, force=force, show_shell_stdout=show_shell_stdout
    )


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

    config = load_config(root)

    if config:
        common.newline()
        common.show(
            "Displaying current dependency versions...", color='message', log=False
        )
        common.newline()
        config.log(datetime.datetime.now().strftime("%F %T"))
        count = 0
        for identity in config.get_dependencies(depth=depth, allow_dirty=allow_dirty):
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

    config = load_config(root)

    if config:
        common.newline()
        common.show("Locking dependencies...", color='message', log=False)
        common.newline()
        count = config.lock_dependencies(*names, obey_existing=False)
        common.dedent(level=0)

    return _display_result("lock", "Locked", count)


@restore_cwd
def delete(*, root=None, force=False, keep_location=False):
    """Delete dependencies for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree
    - `force`: indicates uncommitted changes can be overwritten
    - `keep_location`: delete top level folder or keep the location

    """
    log.info("Deleting dependencies...")
    count = None

    config = load_config(root)

    if config:
        common.newline()
        common.show("Checking for uncommitted changes...", color='message', log=False)
        common.newline()
        count = len(list(config.get_dependencies(allow_dirty=force)))
        common.dedent(level=0)
        common.show("Deleting all dependencies...", color='message', log=False)
        common.newline()
        if keep_location:
            config.clean_dependencies()
        else:
            config.uninstall_dependencies()

    return _display_result("delete", "Deleted", count, allow_zero=True)


def show(*names, root=None):
    """Display the path of an installed dependency or internal file.

    - `name`: dependency name or internal file keyword
    - `root`: specifies the path to the root working tree

    """
    log.info("Finding paths...")

    config = load_config(root)

    if not config:
        log.error("No config found")
        return False

    for name in names or [None]:
        common.show(config.get_path(name), color='path')

    return True


def edit(*, root=None):
    """Open the confuration file for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree

    """
    log.info("Launching config...")

    config = load_config(root)

    if not config:
        log.error("No config found")
        return False

    return system.launch(config.path)


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
    if count is None:
        return False

    assert count == 0
    return allow_zero
