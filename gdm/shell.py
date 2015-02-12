"""Utilities to call shell programs."""

import os
import sys

from sh import Command, ErrorReturnCode


class ShellMixin:

    """Provides classes with shell utilities."""

    INDENT = 2
    indent = 0

    def _mkdir(self, path):
        self._display_in('mkdir', '-p', path)
        os.makedirs(path)

    def _cd(self, path, visible=True):
        if visible:
            self._display_in('cd', path)
        os.chdir(path)

    def _git(self, *args):
        self._call('git', *args, quiet=True)

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
