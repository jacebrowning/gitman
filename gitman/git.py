"""Utilities to call Git commands."""

import os
import logging
from contextlib import suppress
from enum import Enum
from . import common, settings
from .shell import call
from .exceptions import ShellError


log = logging.getLogger(__name__)


def git(*args, **kwargs):
    return call('git', *args, **kwargs)

def gitsvn(*args, **kwargs):
    return call('git', 'svn', *args, **kwargs)

def svn(*args, **kwargs):
    return call('svn', *args, **kwargs)


"""Represnents a repository type"""
class RepoType(Enum):
    UNKNOWN = -1
    GIT = 1
    SVN = 2
    GIT_SVN = 3
    
def _get_local_repotype():
    """Resolves the type of the local repository"""

    repotype = RepoType.UNKNOWN

    # In case of a git repo
    # git show-ref
    # 309189a3dfd8a0132f300c4bf0373efb1a654add refs/heads/master
    # 309189a3dfd8a0132f300c4bf0373efb1a654add refs/remotes/origin/HEAD
    # 309189a3dfd8a0132f300c4bf0373efb1a654add refs/remotes/origin/master
    # f5c86bb39ff8f32feee7d3189546bf29af777fc7 refs/remotes/origin/release/1.0.x
    # fddfe0e02c497ed2847748767a2237c61d847723 refs/tags/release/1.0.0
    #
    # In case of GIT-SVN-REPO
    #git show-ref
    #cd351f6007d1e4d446fe5956dd3e576464e7617c refs/heads/master
    #cd351f6007d1e4d446fe5956dd3e576464e7617c refs/remotes/git-svn

    output = git('show-ref', _show=False, _ignore=True)
    if any('refs/remotes/git-svn' in line for line in output): # check if out contains refs/remotes/git-svn -> GIT_SVN
        repotype = RepoType.GIT_SVN
    elif any('refs/remotes/origin' in line for line in output): # check if output contains refs/remotes/origin -> GIT
        repotype = RepoType.GIT
        
    return repotype

def _get_remote_repotype(repo): 
    """Resolves the type of the remote repository"""

    repotype = RepoType.UNKNOWN

    # git ls-remote git@cupid.lenze.com:Brosche/waf-prototyping-lib.git
    # 519503d686dcf690df3eea051d82a3f99af80805        HEAD
    # 519503d686dcf690df3eea051d82a3f99af80805        refs/heads/master
    # 94ac960c84ceb2542df2b6b7adfe2271ec990d01        refs/tags/release/1.0.0

    #git ls-remote --heads http://svn-ldc/svn/Controls/trunk/XP/TAs/Implementation/i900
    #fatal: unable to access 'http://svn-ldc/svn/Controls/trunk/XP/TAs/Implementation/i900/': The requested URL returned error: 502
    #git ls-remote http://google.de
    #fatal: repository 'http://google.de/' not found

    output = git('ls-remote', repo, _show=False, _ignore=True)
    if any('refs/heads' in line for line in output): # check if output contains refs/heads -> GIT
        repotype = RepoType.GIT    
    elif any('fatal' in line for line in output): # check if output contains fatal -> NOT GIT
        # svn info http://svn-ldc/svn/Controls/trunk/XP/TAs/Implementation/i900
        # Path: i900
        # URL: http://svn-ldc/svn/Controls/trunk/XP/TAs/Implementation/i900
        # Relative URL: ^/trunk/XP/TAs/Implementation/i900
        # Repository Root: http://svn-ldc/svn/Controls
        # Repository UUID: 6cb63ced-a357-0410-a762-939f09bf00c8
        # Revision: 72500
        # Node Kind: directory
        # Last Changed Author: kuehne@lenze.com
        # Last Changed Rev: 72435
        # Last Changed Date: 2018-03-06 14:36:40 +0100 (Tue, 06 Mar 2018)
        output = svn('info', repo, _show=False, _ignore=True)
        if any('UUID' in line for line in output): # check if output contains UUID -> SVN
            repotype = RepoType.SVN

    return repotype





def clone(repo, path, *, cache=settings.CACHE, sparse_paths=None, rev=None):
    """Clone a new Git repository."""
    repotype = _get_remote_repotype(repo)
    log.debug("Clone a new {} repository...".format(str(repotype)))
    
    if repotype == RepoType.GIT:
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
    elif repotype == RepoType.SVN:
        gitsvn('clone', '-r', 'HEAD', repo, path)

def fetch(repo, rev=None):
    """Fetch the latest changes from the remote repository."""

    repotype = _get_local_repotype()
    log.debug("Fetch the latest change from the remote {} repository...".format(str(repotype)))

    if repotype == RepoType.GIT:
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
    elif repotype == RepoType.GIT_SVN and rev:
        gitsvn('rebase', rev)

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

    repotype = _get_local_repotype()
    log.debug("Update the {} repository...".format(str(repotype)))

    git('stash', **hide)
    if clean:
        git('clean', '--force', '-d', '-x', _show=False)

    if repotype == RepoType.GIT:
        rev = _get_sha_from_rev(rev)
        git('checkout', '--force', rev)
        git('branch', '--set-upstream-to', 'origin/' + rev, **hide)

        if fetch:
            # if `rev` was a branch it might be tracking something older
            git('pull', '--ff-only', '--no-rebase', **hide)
    elif repotype == RepoType.GIT_SVN:
        gitsvn('rebase', rev)

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
