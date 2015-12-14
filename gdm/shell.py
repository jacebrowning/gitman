"""Utilities to call shell programs."""

import os
import sys
import logging

from sh import Command, ErrorReturnCode

from . import common

CMD_PREFIX = "$ "
OUT_PREFIX = "> "

log = logging.getLogger(__name__)


def call(name, *args, ignore=False, catch=True, capture=False, visible=True):
    """Call a shell program with arguments."""
    msg = CMD_PREFIX + ' '.join([name] + list(args))
    if visible:
        common.show(msg)
    else:
        log.debug(msg)

    if name == 'cd' and len(args) == 1:
        os.chdir(args[0])
    else:
        try:
            program = Command(name)
            if capture:
                line = program(*args).strip()
                log.debug(OUT_PREFIX + line)
                return line
            else:
                for line in program(*args, _iter='err'):
                    log.debug(OUT_PREFIX + line.strip())
        except ErrorReturnCode as exc:
            msg = "\n  IN: '{}'{}".format(os.getcwd(), exc)
            if ignore:
                log.debug("Ignored error from call to '%s'", name)
            elif catch:
                sys.exit(msg)
            else:
                raise common.CallException(msg)


class ShellMixin:
    """Provides classes with shell utilities."""

    @staticmethod
    def mkdir(path):
        call('mkdir', '-p', path)

    @staticmethod
    def cd(path, visible=True):
        call('cd', path, visible=visible)

    def ln(self, source, target):
        dirpath = os.path.dirname(target)
        if not os.path.isdir(dirpath):
            self.mkdir(dirpath)
        call('ln', '-s', source, target)

    @staticmethod
    def rm(path):
        call('rm', '-rf', path)


class GitMixin:
    """Provides classes with Git utilities."""

    def git_clone(self, repo, path):
        """Clone a new Git repository."""
        self._git('clone', repo, path)

    def git_fetch(self, repo, rev=None):
        """Fetch the latest changes from the remote repository."""
        self._git('remote', 'rm', 'origin', visible=False, ignore=True)
        self._git('remote', 'add', 'origin', repo)
        args = ['fetch', '--tags', '--force', '--prune', 'origin']
        if rev:
            if len(rev) == 40:
                pass  # fetch only works with a SHA if already present locally
            elif '@' in rev:
                pass  # fetch doesn't work with rev-parse
            else:
                args.append(rev)
        self._git(*args)

    def git_changes(self, visible=False):
        """Determine if there are changes in the working tree."""
        try:
            # refresh changes
            self._git('update-index', '-q', '--refresh',
                      visible=False, catch=False)
            # check for uncommitted changes
            self._git('diff-index', '--quiet', 'HEAD',
                      visible=visible, catch=False)
            # check for untracked files
            output = self._git('ls-files', '--others', '--exclude-standard',
                               visible=visible, catch=False, capture=True)
        except common.CallException:
            return True
        else:
            filenames = output.splitlines()
            for filename in filenames:
                log.debug("New file: %s", filename)
            return bool(filenames)

    def git_update(self, rev, clean=True):
        """Update the working tree to the specified revision."""
        hide = {'visible': False, 'ignore': True}
        rev = self._git_get_sha_from_rev(rev)
        self._git('stash', **hide)
        if clean:
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
        return self._git('rev-parse', 'HEAD', capture=True)

    def _git_get_sha_from_rev(self, rev):
        """Get a rev-parse string's hash."""
        if '@{' in rev:  # TODO: use regex for this
            parts = rev.split('@')
            branch = parts[0]
            date = parts[1].strip("{}")
            self._git('checkout', '--force', branch, visible=False)
            rev = self._git('rev-list', '-n', '1', '--before={!r}'.format(date),
                            branch, visible=False, capture=True)
        return rev

    @staticmethod
    def _git(*args, **kwargs):
        return call('git', *args, **kwargs)
