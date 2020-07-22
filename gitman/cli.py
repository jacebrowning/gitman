#!/usr/bin/env python3

"""Command-line interface."""

import argparse
import sys
from typing import Dict, List

import log

from . import __version__, commands, common, exceptions


def main(args=None, function=None):  # pylint: disable=too-many-statements
    """Process command-line arguments and run the program."""

    # Shared options
    debug = argparse.ArgumentParser(add_help=False)
    debug.add_argument(
        '-V', '--version', action='version', version="GitMan v" + __version__
    )
    debug_group = debug.add_mutually_exclusive_group()
    debug_group.add_argument(
        '-v', '--verbose', action='count', default=0, help="enable verbose logging"
    )
    debug_group.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=-1,
        dest='verbose',
        help="only display errors and prompts",
    )
    project = argparse.ArgumentParser(add_help=False)
    project.add_argument(
        '-r', '--root', metavar='PATH', help="root directory of the project"
    )
    depth = argparse.ArgumentParser(add_help=False)
    depth.add_argument(
        '-d',
        '--depth',
        type=common.positive_int,
        default=5,
        metavar="NUM",
        help="limit the number of dependency levels",
    )
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument(
        '-c',
        '--clean',
        action='store_true',
        help="delete ignored files in dependencies",
    )
    options_group = options.add_mutually_exclusive_group()
    options_group.add_argument(
        '-F',
        '--force',
        action='store_true',
        help="overwrite uncommitted changes in dependencies",
    )
    options_group.add_argument(
        '-f',
        '--force-interactive',
        action='store_true',
        dest='force_interactive',
        help="interactively overwrite uncommitted changes in dependencies",
    )
    options_group.add_argument(
        '-s',
        '--skip-changes',
        action='store_true',
        dest='skip_changes',
        help="skip dependencies with uncommitted changes",
    )

    # Main parser
    parser = argparse.ArgumentParser(
        prog='gitman',
        description="A language-agnostic dependency manager using Git.",
        parents=[debug],
        formatter_class=common.WideHelpFormatter,
    )
    subs = parser.add_subparsers(help="", dest='command', metavar="<command>")

    # Init parser
    info = "create a new config file for the project"
    sub = subs.add_parser(
        'init',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug],
        formatter_class=common.WideHelpFormatter,
    )

    # Install parser
    info = "get the specified versions of all dependencies"
    sub = subs.add_parser(
        'install',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project, depth, options],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument('name', nargs='*', help="list of dependencies names to install")
    sub.add_argument(
        '-e', '--fetch', action='store_true', help="always fetch the latest branches"
    )

    # Update parser
    info = "update dependencies to the latest versions"
    sub = subs.add_parser(
        'update',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project, depth, options],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument('name', nargs='*', help="list of dependencies names to update")
    sub.add_argument(
        '-a',
        '--all',
        action='store_true',
        dest='recurse',
        help="also update all nested dependencies",
    )
    sub.add_argument(
        '-L',
        '--skip-lock',
        action='store_false',
        dest='lock',
        default=None,
        help="disable recording of updated versions",
    )

    # List parser
    info = "display the current version of each dependency"
    sub = subs.add_parser(
        'list',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project, depth],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument(
        '-D',
        '--fail-if-dirty',
        action='store_false',
        dest='allow_dirty',
        help="fail if a source has uncommitted changes",
    )

    # Lock parser
    info = "lock the current version of each dependency"
    sub = subs.add_parser(
        'lock',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument('name', nargs='*', help="list of dependency names to lock")

    # Uninstall parser
    info = "delete all installed dependencies"
    sub = subs.add_parser(
        'uninstall',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument(
        '-f',
        '--force',
        action='store_true',
        help="delete uncommitted changes in dependencies",
    )
    sub.add_argument(
        '-k',
        '--keep-location',
        dest='keep_location',
        default=False,
        action='store_true',
        help="keep top level folder location",
    )

    # Show parser
    info = "display the path of a dependency or internal file"
    sub = subs.add_parser(
        'show',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project],
        formatter_class=common.WideHelpFormatter,
    )
    sub.add_argument('name', nargs='*', help="display the path of this dependency")
    sub.add_argument(
        '-c',
        '--config',
        action='store_true',
        help="display the path of the config file",
    )
    sub.add_argument(
        '-l', '--log', action='store_true', help="display the path of the log file"
    )

    # Edit parser
    info = "open the config file in the default editor"
    sub = subs.add_parser(
        'edit',
        description=info.capitalize() + '.',
        help=info,
        parents=[debug, project],
        formatter_class=common.WideHelpFormatter,
    )

    # Parse arguments
    namespace = parser.parse_args(args=args)

    # Configure logging
    common.configure_logging(namespace.verbose)

    # Run the program
    function, args, kwargs = _get_command(function, namespace)
    if function:
        _run_command(function, args, kwargs)
    else:
        parser.print_help()
        sys.exit(1)


def _get_command(function, namespace):  # pylint: disable=too-many-statements
    args: List = []
    kwargs: Dict = {}

    if namespace.command == 'init':
        function = commands.init

    elif namespace.command in ['install', 'update']:
        function = getattr(commands, namespace.command)
        args = namespace.name
        kwargs.update(
            root=namespace.root,
            depth=namespace.depth,
            force=namespace.force,
            force_interactive=namespace.force_interactive,
            clean=namespace.clean,
            skip_changes=namespace.skip_changes,
        )
        if namespace.command == 'install':
            kwargs.update(fetch=namespace.fetch)
        if namespace.command == 'update':
            kwargs.update(recurse=namespace.recurse, lock=namespace.lock)

    elif namespace.command == 'list':
        function = commands.display
        kwargs.update(
            root=namespace.root,
            depth=namespace.depth,
            allow_dirty=namespace.allow_dirty,
        )

    elif namespace.command == 'lock':
        function = getattr(commands, namespace.command)
        args = namespace.name
        kwargs.update(root=namespace.root)

    elif namespace.command == 'uninstall':
        function = commands.delete
        kwargs.update(
            root=namespace.root,
            force=namespace.force,
            keep_location=namespace.keep_location,
        )

    elif namespace.command == 'show':
        function = commands.show
        args = namespace.name
        kwargs.update(root=namespace.root)
        if namespace.config:
            args.append('__config__')
        if namespace.log:
            args.append('__log__')

    elif namespace.command == 'edit':
        function = commands.edit
        kwargs.update(root=namespace.root)

    return function, args, kwargs


def _run_command(function, args, kwargs):
    success = False
    exit_message = None
    try:
        log.debug("Running %s command...", getattr(function, '__name__', 'a'))
        success = function(*args, **kwargs)
    except KeyboardInterrupt:
        log.debug("Command canceled")
    except exceptions.UncommittedChanges as exception:
        _show_error(exception)
        exit_message = (
            "Run again with --force/--force-interactive to discard changes "
            "or '--skip-changes' to skip this dependency"
        )
    except exceptions.ScriptFailure as exception:
        _show_error(exception)
        exit_message = "Run again with '--force' to ignore script errors"
    except exceptions.InvalidConfig as exception:
        _show_error(exception)
        exit_message = "Adapt config and run again"
    finally:
        if exit_message:
            common.show(exit_message, color='message')
            common.newline()

    if success:
        log.debug("Command succeeded")
    else:
        log.debug("Command failed")
        sys.exit(1)


def _show_error(exception):
    common.dedent(0)
    common.newline()
    common.show(str(exception), color='error')
    common.newline()


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
