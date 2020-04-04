#!/usr/bin/env python3

"""Plugin for Git."""

import argparse

from . import __version__, common
from .cli import _get_command, _run_command


PROG = 'git deps'
DESCRIPTION = "Use GitMan (v{}) to install repositories.".format(__version__)


def main(args=None):
    """Process command-line arguments and run the Git plugin."""

    # Main parser
    parser = argparse.ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument(
        '-F',
        '--force',
        action='store_true',
        help="overwrite uncommitted changes in dependencies",
    )
    parser.add_argument(
        '-f',
        '--force-interactive',
        action='store_true',
        dest='force_interactive',
        help="interactively overwrite uncommitted changes in dependencies",
    )
    parser.add_argument(
        '-s',
        '--skip-changes',
        action='store_true',
        dest='skip_changes',
        help="skip dependencies with uncommitted changes",
    )
    parser.add_argument(
        '-c',
        '--clean',
        action='store_true',
        help="delete ignored files when updating dependencies",
    )

    # Options group
    group = parser.add_mutually_exclusive_group()

    # Update option
    group.add_argument(
        '-u',
        '--update',
        const='update',
        help="update dependencies to the latest versions",
        action='store_const',
        dest='command',
    )
    parser.add_argument(
        '-a',
        '--all',
        action='store_true',
        dest='recurse',
        help="include nested dependencies when updating",
    )
    parser.add_argument(
        '-L',
        '--skip-lock',
        action='store_false',
        dest='lock',
        default=True,
        help="disable recording of updated versions",
    )

    # Display option
    group.add_argument(
        '-l',
        '--list',
        const='list',
        help="display the current version of each dependency",
        action='store_const',
        dest='command',
    )

    # Uninstall option
    group.add_argument(
        '-x',
        '--uninstall',
        const='uninstall',
        help="delete all installed dependencies",
        action='store_const',
        dest='command',
    )
    parser.add_argument(
        '-k',
        '--keep-location',
        action='store_true',
        dest='keep_location',
        default=False,
        help='keep top level folder location',
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
    function, args, kwargs = _get_command(None, namespace)
    _run_command(function, args, kwargs)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
