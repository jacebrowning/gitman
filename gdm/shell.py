"""Utilities to call shell programs."""

import os
import sys
import logging

from sh import Command, ErrorReturnCode

logging.getLogger('sh').setLevel(logging.WARNING)


def _call(*args):
    assert args
    args = list(args)
    name = args.pop(0)
    if name == 'mkdir':
        assert len(args) == 2
        assert args.pop(0) == '-p'
        path = args.pop(0)
        os.makedirs(path)
    elif name == 'cd':
        assert len(args) == 1
        path = args.pop(0)
        os.chdir(path)
    else:
        try:
            program = Command(name)
            program(*args)
        except ErrorReturnCode as exc:
            msg = "\n  IN: '{}'{}".format(os.getcwd(), exc)
            sys.exit(msg)


class _Base:

    """Functions to call shell commands."""

    INDENT = 2
    indent = 0

    def _call(self, name, *args):
        self._display_in(*args)
        _call(name, *args)

    def _display_in(self, *args):
        print("{}$ {}".format(' ' * self.indent, ' '.join(args)))


class ShellMixin(_Base):

    """Provides classes with shell utilities."""

    def mkdir(self, path):
        self._display_in('mkdir', '-p', path)
        self._call('mkdir', '-p', path)

    def cd(self, path, visible=True):
        if visible:
            self._display_in('cd', path)
        self._call('cd', path)

    def ln(self, source, target):
        self._call('ln', '-sf', source, target)


class GitMixin(_Base):

    """Provides classes with Git utilities."""

    def git_clone(self, repo, dir):  # pylint: disable=W0622
        """Clone a new working tree."""
        self._clone(repo, dir)

    def git_fetch(self, repo):
        """Fetch the latest changes from the remote repository."""
        self._fetch(repo)

    def git_revert(self):
        """Revert all changes in the working tree."""
        self._clean()
        self._reset()

    def git_update(self, rev):
        """Update the working tree to the specified revision."""
        self._checkout(rev)

    def _git(self, *args):
        self._call('git', *args)

    def _clone(self, repo, dir):  # pylint: disable=W0622
        self._git('clone', repo, dir)

    def _fetch(self, repo):
        self._git('remote', 'remove', 'origin')
        self._git('remote', 'add', 'origin', repo)
        self._git('fetch', '--all', '--tags', '--force', '--prune')

    def _clean(self):
        self._git('clean', '--force', '-d', '-x')

    def _reset(self):
        self._git('reset', '--hard')

    def _checkout(self, rev):
        self._git('checkout', rev)
