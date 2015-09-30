#!/usr/bin/env python3

"""Command-line interface."""

import sys
import argparse

from . import CLI, VERSION, DESCRIPTION
from . import common
from . import commands

log = common.logger(__name__)


def main(args=None, function=None):
    """Process command-line arguments and run the program."""

    # Shared options
    debug = argparse.ArgumentParser(add_help=False)
    debug.add_argument('-V', '--version', action='version', version=VERSION)
    group = debug.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', default=0,
                       help="enable verbose logging")
    group.add_argument('-q', '--quiet', action='store_const', const=-1,
                       dest='verbose', help="only display errors and prompts")
    project = argparse.ArgumentParser(add_help=False)
    project.add_argument('-r', '--root', metavar='PATH',
                         help="root directory of the project")
    shared = {'formatter_class': common.WideHelpFormatter,
              'parents': [project, debug]}

    # Main parser
    parser = argparse.ArgumentParser(prog=CLI, description=DESCRIPTION,
                                     **shared)

    subs = parser.add_subparsers(help="", dest='command', metavar="<command>")

    # Install parser
    info = "get the specified versions of all dependencies"
    sub = subs.add_parser('install', description=info.capitalize() + '.',
                          help=info, **shared)
    sub.add_argument('-f', '--force', action='store_true',
                     help="overwrite uncommitted changes in dependencies")
    sub.add_argument('-c', '--clean', action='store_true',
                     help="keep ignored files in dependencies")

    # Update parser
    info = "update all dependencies to the latest versions"
    sub = subs.add_parser('update', description=info.capitalize() + '.',
                          help=info, **shared)
    # TODO: share these with 'install'
    sub.add_argument('-f', '--force', action='store_true',
                     help="overwrite uncommitted changes in dependencies")
    sub.add_argument('-c', '--clean', action='store_true',
                     help="keep ignored files in dependencies")

    # Display parser
    info = "display the current version of each dependency"
    sub = subs.add_parser('list', description=info.capitalize() + '.',
                          help=info, **shared)
    sub.add_argument('-D', '--no-dirty', action='store_false',
                     dest='allow_dirty',
                     help="fail if a source has uncommitted changes")

    # Uninstall parser
    info = "delete all installed dependencies"
    sub = subs.add_parser('uninstall', description=info.capitalize() + '.',
                          help=info, **shared)
    sub.add_argument('-f', '--force', action='store_true',
                     help="delete uncommitted changes in dependencies")

    # Parse arguments
    args = parser.parse_args(args=args)

    # Configure logging
    common.configure_logging(args.verbose)

    # Run the program
    function, kwargs, exit_msg = _get_command(function, args)
    if function is None:
        parser.print_help()
        sys.exit(1)
    _run_command(function, kwargs, exit_msg)


def _get_command(function, args):
    kwargs = dict(root=args.root)
    exit_msg = ""

    if args.command in ('install', 'update'):
        function = getattr(commands, args.command)
        kwargs.update(dict(force=args.force,
                           clean=args.clean))
        exit_msg = "\n" + "Run again with '--force' to overwrite"
    elif args.command == 'list':
        function = commands.display
        kwargs.update(dict(allow_dirty=args.allow_dirty))
    elif args.command == 'uninstall':
        function = commands.delete
        kwargs.update(dict(force=args.force))
        exit_msg = "\n" + "Run again with '--force' to ignore"

    return function, kwargs, exit_msg


def _run_command(function, kwargs, exit_msg):
    success = False
    try:
        log.debug("running command...")
        success = function(**kwargs)
    except KeyboardInterrupt:
        msg = "command canceled"
        if common.verbosity == common.MAX_VERBOSITY:
            log.exception(msg)
        else:
            log.debug(msg)
    except RuntimeError as exc:
        exit_msg = str(exc) + exit_msg
    else:
        exit_msg = ""
    if success:
        log.debug("command succeeded")
    else:
        log.debug("command failed")
        sys.exit(exit_msg or 1)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
