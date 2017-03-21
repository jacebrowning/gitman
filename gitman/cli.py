#!/usr/bin/env python3

"""Command-line interface."""

import sys
import argparse
import logging

from . import CLI, VERSION, DESCRIPTION
from . import common, exceptions, commands

log = logging.getLogger(__name__)


def main(args=None, function=None):  # pylint: disable=too-many-statements
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
    depth = argparse.ArgumentParser(add_help=False)
    depth.add_argument('-d', '--depth', type=common.positive_int,
                       default=5, metavar="NUM",
                       help="limit the number of dependency levels")
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('-f', '--force', action='store_true',
                         help="overwrite uncommitted changes in dependencies")
    options.add_argument('-c', '--clean', action='store_true',
                         help="delete ignored files in dependencies")
    shared = {'formatter_class': common.WideHelpFormatter}

    # Main parser
    parser = argparse.ArgumentParser(prog=CLI, description=DESCRIPTION,
                                     parents=[debug], **shared)
    subs = parser.add_subparsers(help="", dest='command', metavar="<command>")

    # Init parser
    info = "create a new config file for the project"
    sub = subs.add_parser('init', description=info.capitalize() + '.',
                          help=info, parents=[debug], **shared)

    # Install parser
    info = "get the specified versions of all dependencies"
    sub = subs.add_parser('install', description=info.capitalize() + '.',
                          help=info, parents=[debug, project, depth, options],
                          **shared)
    sub.add_argument('name', nargs='*',
                     help="list of dependencies names to install")
    sub.add_argument('-e', '--fetch', action='store_true',
                     help="always fetch the latest branches")

    # Update parser
    info = "update dependencies to the latest versions"
    sub = subs.add_parser('update', description=info.capitalize() + '.',
                          help=info, parents=[debug, project, depth, options],
                          **shared)
    sub.add_argument('name', nargs='*',
                     help="list of dependencies names to update")
    sub.add_argument('-a', '--all', action='store_true', dest='recurse',
                     help="update all nested dependencies, recursively")
    group = sub.add_mutually_exclusive_group()
    group.add_argument('-l', '--lock',
                       action='store_true', dest='lock', default=None,
                       help="enable recording of versions for later reinstall")
    group.add_argument('-L', '--no-lock',
                       action='store_false', dest='lock', default=None,
                       help="disable recording of versions for later reinstall")

    # List parser
    info = "display the current version of each dependency"
    sub = subs.add_parser('list', description=info.capitalize() + '.',
                          help=info, parents=[debug, project, depth], **shared)
    sub.add_argument('-D', '--no-dirty', action='store_false',
                     dest='allow_dirty',
                     help="fail if a source has uncommitted changes")

    # Lock parser
    info = "lock the current version of each dependency"
    sub = subs.add_parser('lock', description=info.capitalize() + '.',
                          help=info, parents=[debug, project], **shared)
    sub.add_argument('name', nargs='*',
                     help="list of dependency names to lock")

    # Uninstall parser
    info = "delete all installed dependencies"
    sub = subs.add_parser('uninstall', description=info.capitalize() + '.',
                          help=info, parents=[debug, project], **shared)
    sub.add_argument('-f', '--force', action='store_true',
                     help="delete uncommitted changes in dependencies")

    # Show parser
    info = "display the path of a dependency or internal file"
    sub = subs.add_parser('show', description=info.capitalize() + '.',
                          help=info, parents=[debug, project], **shared)
    sub.add_argument('name', nargs='*',
                     help="display the path of this dependency")
    sub.add_argument('-c', '--config', action='store_true',
                     help="display the path of the config file")
    sub.add_argument('-l', '--log', action='store_true',
                     help="display the path of the log file")

    # Edit parser
    info = "open the config file in the default editor"
    sub = subs.add_parser('edit', description=info.capitalize() + '.',
                          help=info, parents=[debug, project], **shared)

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
    args = []
    kwargs = {}

    if namespace.command == 'init':
        function = commands.init

    elif namespace.command in ['install', 'update']:
        function = getattr(commands, namespace.command)
        args = namespace.name
        kwargs.update(root=namespace.root,
                      depth=namespace.depth,
                      force=namespace.force,
                      clean=namespace.clean)
        if namespace.command == 'install':
            kwargs.update(fetch=namespace.fetch)
        if namespace.command == 'update':
            kwargs.update(recurse=namespace.recurse,
                          lock=namespace.lock)

    elif namespace.command == 'list':
        function = commands.display
        kwargs.update(root=namespace.root,
                      depth=namespace.depth,
                      allow_dirty=namespace.allow_dirty)

    elif namespace.command == 'lock':
        function = getattr(commands, namespace.command)
        args = namespace.name
        kwargs.update(root=namespace.root)

    elif namespace.command == 'uninstall':
        function = commands.delete
        kwargs.update(root=namespace.root,
                      force=namespace.force)

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
        exit_message = "Run again with '--force' to discard changes"
    except exceptions.ScriptFailure as exception:
        _show_error(exception)
        exit_message = "Run again with '--force' to ignore script errors"
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
    # TODO: require level=, evaluate all calls to dedent()
    common.dedent(0)
    common.newline()
    common.show(str(exception), color='error')
    common.newline()


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
