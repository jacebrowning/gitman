"""Utilities to call shell programs."""

import os
import sys
import logging

from sh import Command, ErrorReturnCode

from . import common

logging.getLogger('sh').setLevel(logging.WARNING)
log = common.logger(__name__)


def _call(name, *args, ignore=False, catch=True, capture=False):
    """Call a shell program with arguments."""
    if name == 'cd' and len(args) == 1:
        os.chdir(args[0])
    else:
        try:
            program = Command(name)
            if capture:
                return program(*args).strip()
            else:
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

    def _call(self, *args,
              visible=True, catch=True, ignore=False, capture=False):
        if visible:
            self._display_in(*args)
        log.debug("running: %s", ' '.join(args))
        return _call(*args, catch=catch, ignore=ignore, capture=capture)

    def _display_in(self, *args):
        common.show("{}$ {}".format(' ' * self.indent, ' '.join(args)))


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
        if rev and len(rev) != 40:  # fetch doesn't work with SHAs
            args.append(rev)
        self._git(*args)

    def git_changes(self):
        """Determine if there are changes in the working tree."""
        try:
            # refresh changes
            self._git('update-index', '-q', '--refresh',
                      visible=False, catch=False)
            # check for uncommitted changes
            self._git('diff-index', '--quiet', 'HEAD',
                      visible=False, catch=False)
            # check for untracked files
            output = self._git('ls-files', '--others', '--exclude-standard',
                               visible=False, catch=False, capture=True)
        except common.CallException:
            return True
        else:
            filenames = output.splitlines()
            for filename in filenames:
                log.debug("new file: %s", filename)
            return bool(filenames)

    def git_update(self, rev):
        """Update the working tree to the specified revision."""
        hide = {'visible': False, 'ignore': True}
        self._git('stash', **hide)
        self._git('clean', '--force', '-d', '-x', visible=False)
        self._git('checkout', '--force', rev)
        self._git('branch', '--set-upstream-to', 'origin/' + rev, **hide)
        self._git('pull', '--ff-only', '--no-rebase', **hide)

    def git_get_url(self):
        """Get the current repository's URL."""
        return self._git('config', '--get', 'remote.origin.url',
                         visible=False, capture=True)

    def git_get_sha(self):
        """Get the current working tree's hash."""
        return self._git('rev-parse', 'HEAD', visible=False, capture=True)

    def _git(self, *args, **kwargs):
        return self._call('git', *args, **kwargs)
