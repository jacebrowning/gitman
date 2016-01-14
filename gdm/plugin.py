#!/usr/bin/env python3

"""Plugin for Git."""

import argparse
import logging

from . import PLUGIN, NAME, __version__
from . import common
from .cli import _get_command, _run_command

PROG = 'git ' + PLUGIN
DESCRIPTION = "Use {} (v{}) to install repostories.".format(NAME, __version__)

log = logging.getLogger(__name__)


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
        help="update dependencies to the latest versions", **shared
    )
    parser.add_argument('-a', '--all', action='store_true', dest='recurse',
                        help="include nested dependencies when updating")
    parser.add_argument('-L', '--no-lock',
                        action='store_false', dest='lock', default=True,
                        help="skip recording of versions for later reinstall")

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
    namespace = parser.parse_args(args=args)

    # Modify arguments to match CLI interface
    if not namespace.command:
        namespace.command = 'install'
    namespace.name = []
    namespace.root = None
    namespace.depth = None
    namespace.allow_dirty = True
    namespace.fetch = True

    # Configure logging
    common.configure_logging()

    # Run the program
    function, args, kwargs, exit_msg = _get_command(None, namespace)
    _run_command(function, args, kwargs, exit_msg)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
