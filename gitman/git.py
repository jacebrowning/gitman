"""Utilities to call Git commands."""

import os
import logging
from contextlib import suppress

from . import common
from .shell import call
from .exceptions import ShellError


log = logging.getLogger(__name__)


def git(*args, **kwargs):
    return call('git', *args, **kwargs)


def clone(repo, path, *, cache=None):
    """Clone a new Git repository."""
    log.debug("Creating a new repository...")

    cache = cache or os.path.expanduser("~/.gitcache")
    cache = os.path.normpath(cache)

    name = repo.split('/')[-1]
    if name.endswith(".git"):
        name = name[:-4]

    reference = os.path.join(cache, name + ".reference")
    if not os.path.isdir(reference):
        git('clone', '--mirror', repo, reference)

    git('clone', '--reference', reference, repo, os.path.normpath(path))


def fetch(repo, rev=None):
    """Fetch the latest changes from the remote repository."""
    git('remote', 'set-url', 'origin', repo)
    args = ['fetch', '--tags', '--force', '--prune', 'origin']
    if rev:
        if len(rev) == 40:
            pass  # fetch only works with a SHA if already present locally
        elif '@' in rev:
            pass  # fetch doesn't work with rev-parse
        else:
            args.append(rev)
    git(*args)


def valid():
    """Confirm the current directory is a valid working tree."""
    log.debug("Checking for a valid working tree...")

    try:
        git('rev-parse', '--is-inside-work-tree', _show=False)
    except ShellError:
        return False
    else:
        return True


def changes(include_untracked=False, display_status=True, _show=False):
    """Determine if there are changes in the working tree."""
    status = False

    try:
        # Refresh changes
        git('update-index', '-q', '--refresh', _show=False)

        # Check for uncommitted changes
        git('diff-index', '--quiet', 'HEAD', _show=_show)

        # Check for untracked files
        lines = git('ls-files', '--others', '--exclude-standard', _show=_show)

    except ShellError:
        status = True

    else:
        status = bool(lines) and include_untracked

    if status and display_status:
        with suppress(ShellError):
            lines = git('status', _show=True)
            common.show(*lines, color='git_changes')

    return status


def update(rev, *, clean=True, fetch=False):  # pylint: disable=redefined-outer-name
    """Update the working tree to the specified revision."""
    hide = {'_show': False, '_ignore': True}

    git('stash', **hide)
    if clean:
        git('clean', '--force', '-d', '-x', _show=False)

    rev = _get_sha_from_rev(rev)
    git('checkout', '--force', rev)
    git('branch', '--set-upstream-to', 'origin/' + rev, **hide)

    if fetch:
        # if `rev` was a branch it might be tracking something older
        git('pull', '--ff-only', '--no-rebase', **hide)


def get_url():
    """Get the current repository's URL."""
    return git('config', '--get', 'remote.origin.url', _show=False)[0]


def get_hash(_show=False):
    """Get the current working tree's hash."""
    return git('rev-parse', 'HEAD', _show=_show)[0]


def get_tag():
    """Get the current working tree's tag (if on a tag)."""
    return git('describe', '--tags', '--exact-match',
               _show=False, _ignore=True)[0]


def get_branch():
    """Get the current working tree's branch."""
    return git('rev-parse', '--abbrev-ref', 'HEAD', _show=False)[0]


def _get_sha_from_rev(rev):
    """Get a rev-parse string's hash."""
    if '@{' in rev:  # TODO: use regex for this
        parts = rev.split('@')
        branch = parts[0]
        date = parts[1].strip("{}")
        git('checkout', '--force', branch, _show=False)
        rev = git('rev-list', '-n', '1', '--before={!r}'.format(date),
                  branch, _show=False)[0]
    return rev
