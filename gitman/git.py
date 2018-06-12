"""Utilities to call Git commands."""

import os
import shutil

import logging
from contextlib import suppress

from . import common, settings
from .shell import call
from .exceptions import ShellError


log = logging.getLogger(__name__)


def git(*args, **kwargs):
    return call('git', *args, **kwargs)

def gitsvn(*args, **kwargs):
    return call('git', 'svn', *args, **kwargs)

def clean_dir(path):    
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def clone(type, repo, path, *, cache=settings.CACHE, sparse_paths=None, rev=None):
    """Clone a new Git repository."""
    log.debug("Creating a new repository...")

    if type == 'git':
        name = repo.split('/')[-1]
        if name.endswith(".git"):
            name = name[:-4]

        reference = os.path.join(cache, name + ".reference")
        if not os.path.isdir(reference):
            git('clone', '--mirror', repo, reference)

        normpath = os.path.normpath(path)
        if sparse_paths:
            os.mkdir(normpath)
            git('-C', normpath, 'init')
            git('-C', normpath, 'config', 'core.sparseCheckout', 'true')
            git('-C', normpath, 'remote', 'add', '-f', 'origin', reference)

            with open("%s/%s/.git/info/sparse-checkout" % (os.getcwd(), normpath), 'w') as fd:
                fd.writelines(sparse_paths)
            with open("%s/%s/.git/objects/info/alternates" % (os.getcwd(), normpath), 'w') as fd:
                fd.write("%s/objects" % reference)

            # We use directly the revision requested here in order to respect,
            # that not all repos have `master` as their default branch
            git('-C', normpath, 'pull', 'origin', rev)
        else:
            git('clone', '--reference', reference, repo, os.path.normpath(path))
    elif type == 'git-svn':
        # just the preperation for the svn deep clone / checkout here (clone will be made in update function to simplify source.py).
        os.makedirs(path)


def fetch(type, repo, rev=None):
    """Fetch the latest changes from the remote repository."""
    
    if type == 'git':
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
    #elif type == 'git-svn':
        #deep clone made in update function

def valid():
    """Confirm the current directory is a valid working tree."""
    log.debug("Checking for a valid working tree...")

    try:
        git('rev-parse', '--is-inside-work-tree', _show=False)
    except ShellError:
        return False
    else:
        return True


def changes(type, include_untracked=False, display_status=True, _show=False):
    """Determine if there are changes in the working tree."""
    status = False

    if type == 'git':
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


def update(type, repo, path, *, clean=True, fetch=False, rev=None):  # pylint: disable=redefined-outer-name
 
    if type == 'git':
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
    elif type == 'git-svn':
        # make deep clone here for simplification of sources.py
        # and to realize consistent readonly clone (always forced)
        clean_dir('.')
        gitsvn('clone', '-r', rev, repo, '.')


def get_url(type):
    """Get the current repository's URL."""
    if type == 'git':
        return git('config', '--get', 'remote.origin.url', _show=False)[0]
    elif type == 'git-svn':
        return git('config', '--get', 'svn-remote.svn.url', _show=False)[0]


def get_hash(type, _show=False):
    """Get the current working tree's hash."""
    if type == 'git':
        return git('rev-parse', 'HEAD', _show=_show)[0]
    elif type == 'git-svn':
        return ''.join(filter(str.isdigit, gitsvn('info', _show=_show)[4]))

def get_tag():
    """Get the current working tree's tag (if on a tag)."""
    return git('describe', '--tags', '--exact-match',
               _show=False, _ignore=True)[0]

def is_fetch_required(type, rev):
    if type == 'git':
        return rev not in (get_branch(),
                           get_hash(type),
                           get_tag())
    return False

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
