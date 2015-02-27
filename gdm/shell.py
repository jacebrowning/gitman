"""Utilities to call shell programs."""

import os
import sys
import logging

from sh import Command, ErrorReturnCode

from . import common

logging.getLogger('sh').setLevel(logging.WARNING)
log = common.logger(__name__)


def _call(name, *args, catch=True):
    """Call a shell program with arguments."""
    if name == 'mkdir' and len(args) == 2 and args[0] == '-p':
        os.makedirs(args[1])
    elif name == 'cd' and len(args) == 1:
        os.chdir(args[0])
    else:
        try:
            program = Command(name)
            program(*args)
        except ErrorReturnCode as exc:
            msg = "\n  IN: '{}'{}".format(os.getcwd(), exc)
            if catch:
                sys.exit(msg)
            else:
                raise common.CallException(msg)


class _Base:

    """Functions to call shell commands."""

    INDENT = 2
    indent = 0

    def _call(self, *args, visible=True, catch=True):
        if visible:
            self._display_in(*args)
        _call(*args, catch=catch)

    def _display_in(self, *args):
        print("{}$ {}".format(' ' * self.indent, ' '.join(args)))


class ShellMixin(_Base):

    """Provides classes with shell utilities."""

    def mkdir(self, path):
        self._call('mkdir', '-p', path)

    def cd(self, path, visible=True):
        self._call('cd', path, visible=visible)

    def ln(self, source, target):
        dirpath = os.path.dirname(target)
        if not os.path.isdir(dirpath):
            self.mkdir(dirpath)
        self._call('ln', '-s', source, target)


class GitMixin(_Base):

    """Provides classes with Git utilities."""

    def git_clone(self, repo, dir):  # pylint: disable=W0622
        """Clone a new working tree."""
        self._clone(repo, dir)

    def git_fetch(self, repo):
        """Fetch the latest changes from the remote repository."""
        self._fetch(repo)

    def git_changes(self):
        """Determine if there are changes in the working tree."""
        try:
            kwargs = {'visible': False, 'catch': False}
            self._git('diff-files', '--quiet', **kwargs)
            self._git('diff-index', '--cached', '--quiet', 'HEAD', **kwargs)
        except common.CallException as exc:
            log.debug(exc)
            return True
        else:
            return False

    def git_revert(self):
        """Revert all changes in the working tree."""
        self._stash(visible=False)
        self._reset()
        self._clean(visible=False)

    def git_update(self, rev):
        """Update the working tree to the specified revision."""
        self._checkout(rev)

    def _git(self, *args, **kwargs):
        self._call('git', *args, **kwargs)

    def _clone(self, repo, dir):  # pylint: disable=W0622
        self._git('clone', repo, dir)

    def _fetch(self, repo):
        self._git('remote', 'remove', 'origin', visible=False)
        self._git('remote', 'add', 'origin', repo)
        self._git('fetch', '--all', '--tags', '--force', '--prune')

    def _stash(self, visible=True):
        self._git('stash', visible=visible)

    def _clean(self, visible=True):
        self._git('clean', '--force', '-d', '-x', visible=visible)

    def _reset(self):
        self._git('reset', '--hard')

    def _checkout(self, rev):
        self._git('checkout', rev)
