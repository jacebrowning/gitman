#!/usr/bin/env python3

"""Plugin for Git."""

import argparse

from . import PLUGIN, __version__
from . import common
from .cli import _get_command, _run_command

PROG = 'git ' + PLUGIN
DESCRIPTION = "Use GDM (v{}) to manage source dependencies.".format(__version__)

log = common.logger(__name__)


def main(args=None):
    """Process command-line arguments and run the Git plugin."""

    # Main parser
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument(
        '-f', '--force', action='store_true',
        help="overwrite uncommitted changes in dependencies",
    )
    parser.add_argument(
        '-c', '--clean', action='store_true',
        help="keep ignored files when updating dependencies",
    )

    # Options group
    group = parser.add_mutually_exclusive_group()
    shared = dict(action='store_const', dest='command')

    # Update option
    group.add_argument(
        '-u', '--update', const='update',
        help="update all dependencies to the latest versions", **shared
    )

    # Display option
    group.add_argument(
        '-l', '--list', const='list',
        help="display the current version of each dependency", **shared
    )

    # Uninstall option
    group.add_argument(
        '-x', '--uninstall', const='uninstall',
        help="delete all installed dependencies", **shared
    )

    # Parse arguments
    args = parser.parse_args(args=args)

    # Modify arguments to match CLI interface
    if not args.command:
        args.command = 'install'
    args.root = None
    args.allow_dirty = True

    # Configure logging
    common.configure_logging()

    # Run the program
    function, kwargs, exit_msg = _get_command(None, args)
    _run_command(function, kwargs, exit_msg)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
