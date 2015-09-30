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
    parser.add_argument('-f', '--force', action='store_true',
                        help="overwrite uncommitted changes in dependencies")
    parser.add_argument('-C', '--no-clean', action='store_false', dest='clean',
                        help="keep ignored files when updating dependencies")
    group = parser.add_mutually_exclusive_group()

    # Update option
    info = "update all dependencies to the latest versions"
    group.add_argument('-u', '--update', action='store_const', const='update',
                       dest='command', help=info)

    # Display option
    info = "display the current version of each dependency"
    group.add_argument('-l', '--list', action='store_const', const='list',
                       dest='command', help=info)

    # Uninstall option
    info = "delete all installed dependencies"
    group.add_argument('-x', '--uninstall', action='store_const',
                       const='uninstall', dest='command', help=info)

    # Parse arguments
    args = parser.parse_args(args=args)
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
