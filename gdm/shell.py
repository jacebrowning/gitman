"""Utilities to call shell programs."""

import os
import sys
import subprocess
import logging

from sh import Command, ErrorReturnCode

from . import common

logging.getLogger('sh').setLevel(logging.WARNING)
log = common.logger(__name__)


def _call(name, *args, ignore=False, catch=True):
    """Call a shell program with arguments."""
    if name == 'cd' and len(args) == 1:
        os.chdir(args[0])
    else:
        try:
            program = Command(name)
            for line in program(*args, _iter='err'):
                log.debug(line.strip())
        except ErrorReturnCode as exc:
            msg = "\n  IN: '{}'{}".format(os.getcwd(), exc)
            if ignore:
                log.debug("ignored error from call to '%s'", name)
            elif catch:
                sys.exit(msg)
            else:
                raise common.CallException(msg)


class _Base:

    """Functions to call shell commands."""

    INDENT = 2
    indent = 0

    def _call(self, *args, visible=True, catch=True, ignore=True):
        if visible:
            self._display_in(*args)
        _call(*args, catch=catch, ignore=ignore)

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

    def git_create(self):
        """Initialize a new Git repository."""
        self._git('init')

    def git_fetch(self, repo, rev=None):
        """Fetch the latest changes from the remote repository."""
        self._git('remote', 'remove', 'origin', visible=False, ignore=True)
        self._git('remote', 'add', 'origin', repo)
        args = ['fetch', '--tags', '--force', '--prune', 'origin']
        if rev:
            args.append(rev)
        self._git(*args)

    def git_changes(self):
        """Determine if there are changes in the working tree."""
        try:
            kwargs = {'visible': False, 'catch': False}
            self._git('update-index', '-q', '--refresh', **kwargs)
            self._git('diff-files', '--quiet', **kwargs)
            self._git('diff-index', '--cached', '--quiet', 'HEAD', **kwargs)
        except common.CallException:
            return True
        else:
            return False

    def git_update(self, rev):
        """Update the working tree to the specified revision."""
        self._git('stash', visible=False, ignore=True)
        self._git('clean', '--force', '-d', '-x', visible=False)
        subprocess.call("for remote in `git branch -r | grep -v master `; "
                        "do git checkout --track $remote ; done", shell=True,
                        stderr=subprocess.PIPE)
        self._git('reset', '--hard', rev)

    def _git(self, *args, **kwargs):
        self._call('git', *args, **kwargs)
