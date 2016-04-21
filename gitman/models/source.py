"""Wrappers for the dependency configuration files."""

import os
import logging

import yorm
from yorm.types import String, AttributeDictionary

from .. import common
from .. import git
from .. import shell
from ..exceptions import InvalidConfig, InvalidRepository, UncommittedChanges


log = logging.getLogger(__name__)


@yorm.attr(name=String)
@yorm.attr(link=String)
@yorm.attr(repo=String)
@yorm.attr(rev=String)
class Source(AttributeDictionary):
    """A dictionary of `git` and `ln` arguments."""

    DIRTY = '<dirty>'
    UNKNOWN = '<unknown>'

    def __init__(self, repo, name, rev='master', link=None):
        super().__init__()
        self.repo = repo
        self.name = name
        self.rev = rev
        self.link = link
        if not self.repo:
            raise InvalidConfig("'repo' missing on {}".format(repr(self)))
        if not self.name:
            raise InvalidConfig("'name' missing on {}".format(repr(self)))

    def __repr__(self):
        return "<source {}>".format(self)

    def __str__(self):
        fmt = "'{r}' @ '{v}' in '{d}'"
        if self.link:
            fmt += " <- '{s}'"
        return fmt.format(r=self.repo, v=self.rev, d=self.name, s=self.link)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name

    def update_files(self, force=False, fetch=False, clean=True):
        """Ensure the source matches the specified revision."""
        log.info("Updating source files...")

        # Enter the working tree
        if not os.path.exists(self.name):
            log.debug("Creating a new repository...")
            git.clone(self.repo, self.name)
        shell.cd(self.name)

        # Check for uncommitted changes
        if not force:
            log.debug("Confirming there are no uncommitted changes...")
            if git.changes(include_untracked=clean):
                common.show()
                msg = "Uncommitted changes: {}".format(os.getcwd())
                raise UncommittedChanges(msg)

        # Fetch the desired revision
        if fetch or self.rev not in (git.get_branch(),
                                     git.get_hash(),
                                     git.get_tag()):
            git.fetch(self.repo, self.rev)

        # Update the working tree to the desired revision
        git.update(self.rev, fetch=fetch, clean=clean)

    def create_link(self, root, force=False):
        """Create a link from the target name to the current directory."""
        if self.link:
            log.info("Creating a symbolic link...")
            target = os.path.join(root, self.link)
            source = os.path.relpath(os.getcwd(), os.path.dirname(target))
            if os.path.islink(target):
                os.remove(target)
            elif os.path.exists(target):
                if force:
                    shell.rm(target)
                else:
                    common.show()
                    msg = "Preexisting link location: {}".format(target)
                    raise UncommittedChanges(msg)
            shell.ln(source, target)

    def identify(self, allow_dirty=True, allow_missing=True):
        """Get the path and current repository URL and hash."""
        if os.path.isdir(self.name):

            shell.cd(self.name)

            path = os.getcwd()
            url = git.get_url()
            if git.changes(display_status=not allow_dirty, _show=True):
                revision = self.DIRTY
                if not allow_dirty:
                    common.show()
                    msg = "Uncommitted changes: {}".format(os.getcwd())
                    raise UncommittedChanges(msg)
            else:
                revision = git.get_hash(_show=True)
            common.show(revision, log=False)

            return path, url, revision

        elif allow_missing:

            return os.getcwd(), '<missing>', self.UNKNOWN

        else:

            path = os.path.join(os.getcwd(), self.name)
            msg = "Not a valid repository: {}".format(path)
            raise InvalidRepository(msg)

    def lock(self):
        """Return a locked version of the current source."""
        _, _, revision = self.identify(allow_missing=False)
        source = self.__class__(self.repo, self.name, revision, self.link)
        return source
