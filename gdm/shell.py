"""Utilities to call shell programs."""

import os
import sys

from sh import Command, ErrorReturnCode


class _Base:

    """Functions to call shell commands."""

    INDENT = 2
    indent = 0

    def _call(self, name, *args, quiet=False):
        self._display_in(*args)

        if quiet:
            args = list(args) + ['--quiet']

        try:
            program = Command(name)
            program(*args)
        except ErrorReturnCode as exc:
            msg = "\n  IN: '{}'{}".format(os.getcwd(), exc)
            sys.exit(msg)

    def _display_in(self, *args):
        print("{}$ {}".format(' ' * self.indent, ' '.join(args)))


class ShellMixin(_Base):

    """Provides classes with shell utilities."""

    def _mkdir(self, path):
        self._display_in('mkdir', '-p', path)
        os.makedirs(path)

    def _cd(self, path, visible=True):
        if visible:
            self._display_in('cd', path)
        os.chdir(path)

    def _link(self, source, target):
        self._call('ln', '-sf', source, target)


class GitMixin(_Base):

    """Provides classes with Git utilities."""

    def _git(self, *args):
        self._call('git', *args, quiet=True)

    def _fetch(self, repo):
        self._git('fetch', repo, '--tags', '--force', '--prune')

    def _clean(self):
        self._git('clean', '--force', '-d', '-x')

    def _reset(self):
        self._git('reset', '--hard')

    def _clone(self, repo, dir):  # pylint: disable=W0622
        self._git('clone', repo, dir)

    def _checkout(self, rev):
        self._git('checkout', rev)
