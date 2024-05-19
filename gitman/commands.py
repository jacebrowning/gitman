"""Functions to manage the installation of dependencies."""

import datetime

import log
from startfile import startfile

from . import common
from .decorators import preserve_cwd
from .models import Config, Source, find_nested_configs, load_config
from .models.config import filter_nested_configs


def init(*, force: bool = False):
    """Create a new config file for the project.

    Optional arguments:

    - `force`: indicates config file should always be generated

    """
    success = False

    config = load_config()

    if config and not force:
        msg = "Configuration file already exists: {}".format(config.path)
        common.show(msg, color="error")

    else:
        config = Config()
        source = Source(
            repo="https://github.com/githubtraining/hellogitworld",
            name="sample_dependency",
            rev="master",
        )
        config.sources.append(source)
        source = source.lock(  # type: ignore
            rev="ebbbf773431ba07510251bb03f9525c7bab2b13a", verify_rev=False
        )
        config.sources_locked.append(source)
        config.datafile.save()

        msg = "Created sample config file: {}".format(config.path)
        common.show(msg, color="success")
        success = True

    msg = "To edit this config file, run: gitman edit"
    common.show(msg, color="message")

    return success


@preserve_cwd
def install(
    *names,
    root=None,
    depth=None,
    force=False,
    fetch=False,
    force_interactive=False,
    clean=True,
    skip_changes=False,
    skip_default_group=False,
    skip_scripts=False,
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
    - `skip_default_group`: indicates default_group should be skipped if
     `*names` is empty
    - `skip_scripts`: indicates scripts should be skipped
    """
    log.info(
        "%sInstalling dependencies: %s",
        "force-" if force or force_interactive else "",
        ", ".join(names) if names else "<all>",
    )
    count = None

    config = load_config(root)
    configs = [config] if config else []
    configs.extend(find_nested_configs(root, depth, []))
    configs = filter_nested_configs(configs)

    if configs:
        count = 0
        common.newline()

    for index, config in enumerate(configs):
        label = "nested dependencies" if index else "dependencies"
        common.show(f"Installing {label}...", color="message", log=False)
        common.newline()

        _count = config.install_dependencies(
            *names,
            update=False,
            depth=depth,
            force=force,
            force_interactive=force_interactive,
            fetch=fetch,
            clean=clean,
            skip_changes=skip_changes,
            skip_default_group=skip_default_group,
        )
        count += _count  # type: ignore

        if _count and not skip_scripts:
            label = "nested scripts" if index else "scripts"
            common.show(f"Running {label}...", color="message", log=False)
            common.newline()
            config.run_scripts(*names, depth=depth, force=force, show_shell_stdout=True)

    return _display_result("install", "Installed", count)


@preserve_cwd
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
    skip_default_group=False,
    skip_scripts=False,
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
    - `skip_default_group`: indicates default_group should be skipped if
     `*names` is empty
    - `skip_scripts`: indicates scripts should be skipped
    """
    log.info(
        "%s dependencies%s: %s",
        "Force updating" if force or force_interactive else "Updating",
        ", recursively" if recurse else "",
        ", ".join(names) if names else "<all>",
    )
    count = None

    config = load_config(root)
    configs = [config] if config else []
    configs.extend(find_nested_configs(root, depth, []))

    if configs:
        count = 0
        common.newline()

    for index, config in enumerate(configs):
        label = "nested dependencies" if index else "dependencies"
        common.show(f"Updating {label}...", color="message", log=False)
        common.newline()
        _count = config.install_dependencies(
            *names,
            update=True,
            depth=depth,
            recurse=recurse,
            force=force,
            force_interactive=force_interactive,
            fetch=True,
            clean=clean,
            skip_changes=skip_changes,
            skip_default_group=skip_default_group,
        )
        count += _count  # type: ignore

        if _count and lock is not False:
            common.show("Recording installed versions...", color="message", log=False)
            common.newline()
            config.lock_dependencies(
                *names,
                obey_existing=lock is None,
                skip_changes=skip_changes or force_interactive,
            )

        if _count and not skip_scripts:
            label = "nested scripts" if index else "scripts"
            common.show(f"Running {label}...", color="message", log=False)
            common.newline()
            config.run_scripts(*names, depth=depth, force=force, show_shell_stdout=True)

    return _display_result("update", "Updated", count)


@preserve_cwd
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

    if config and config.root:
        common.newline()
        common.show(
            "Displaying current dependency versions...", color="message", log=False
        )
        common.newline()
        config.log(datetime.datetime.now().strftime("%F %T"))
        count = 0

        skip_paths = []
        for identity in config.get_dependencies(depth=depth, allow_dirty=allow_dirty):
            count += 1
            config.log("{}: {} @ {}", *identity)
            skip_paths.append(identity.path)

        nested_configs = find_nested_configs(config.root, depth, skip_paths)
        if nested_configs:
            common.show(
                "Displaying nested dependency versions...", color="message", log=False
            )
            common.newline()
            for nested_config in nested_configs:
                for identity in nested_config.get_dependencies(
                    depth=depth, allow_dirty=allow_dirty
                ):
                    count += 1
                    config.log("{}: {} @ {}", *identity)

        config.log()

    return _display_result("display", "Displayed", count)


@preserve_cwd
def lock(*names, depth=None, root=None):
    """Lock current dependency versions for a project.

    Optional arguments:

    - `*names`: optional list of dependency directory names to filter on
    - `depth`: number of levels of dependencies to traverse
    - `root`: specifies the path to the root working tree

    """
    log.info("Locking dependencies...")
    count = None

    config = load_config(root)
    configs = [config] if config else []
    configs.extend(find_nested_configs(root, depth, []))
    configs = filter_nested_configs(configs)
    if configs:
        count = 0
        common.newline()

    for config in configs:
        common.show("Locking dependencies...", color="message", log=False)
        common.newline()
        count += config.lock_dependencies(*names, obey_existing=False)  # type: ignore
        common.dedent(level=0)

    return _display_result("lock", "Locked", count)


@preserve_cwd
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
        common.show("Checking for uncommitted changes...", color="message", log=False)
        common.newline()
        count = len(list(config.get_dependencies(allow_dirty=force)))
        common.dedent(level=0)
        common.show("Deleting all dependencies...", color="message", log=False)
        common.newline()
        if keep_location or config.location == ".":
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
        common.show(config.get_path(name), color="path")

    return True


def edit(*, root=None):
    """Open the configuration file for a project.

    Optional arguments:

    - `root`: specifies the path to the root working tree

    """
    log.info("Launching config...")
    config = load_config(root)

    if not config:
        log.error("No config found")
        return False

    return startfile(config.path)


def _display_result(modify, modified, count, allow_zero=False):
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
        common.show(f"No dependencies to {modify}", color="error")
    elif count == 1:
        common.show(f"{modified} 1 dependency", color="message")
    else:
        common.show(f"{modified} {count} dependencies", color="message")
    common.newline()

    if count:
        return True
    if count is None:
        return False

    assert count == 0
    return allow_zero
