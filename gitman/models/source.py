import logging
import os
import warnings

import yorm
from yorm.types import AttributeDictionary, List, NullableString, String

from .. import common, exceptions, git, shell


log = logging.getLogger(__name__)


@yorm.attr(name=String)
@yorm.attr(type=String)
@yorm.attr(repo=String)
@yorm.attr(sparse_paths=List.of_type(String))
@yorm.attr(rev=String)
@yorm.attr(link=NullableString)
@yorm.attr(scripts=List.of_type(String))
class Source(AttributeDictionary):
    """A dictionary of `git` and `ln` arguments."""

    DIRTY = '<dirty>'
    UNKNOWN = '<unknown>'

    def __init__(self, type, repo, name=None, rev='master',
                 link=None, scripts=None, sparse_paths=None):

        super().__init__()
        self.type = type or 'git'
        self.repo = repo
        self.name = self._infer_name(repo) if name is None else name
        self.rev = rev
        self.link = link
        self.scripts = scripts or []
        self.sparse_paths = sparse_paths or []

        for key in ['name', 'repo', 'rev']:
            if not self[key]:
                msg = "'{}' required for {}".format(key, repr(self))
                raise exceptions.InvalidConfig(msg)

    def _on_post_load(self):
        self.type = self.type or 'git'

    def __repr__(self):
        return "<source {}>".format(self)

    def __str__(self):
        pattern = "['{t}'] '{r}' @ '{v}' in '{d}'"
        if self.link:
            pattern += " <- '{s}'"
        return pattern.format(t=self.type, r=self.repo,
                              v=self.rev, d=self.name, s=self.link)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name

    def update_files(self, force=False, fetch=False, clean=True):
        """Ensure the source matches the specified revision."""
        log.info("Updating source files...")

        # Clone the repository if needed
        if not os.path.exists(self.name):
            git.clone(self.type, self.repo, self.name,
                      sparse_paths=self.sparse_paths, rev=self.rev)

        # Enter the working tree
        shell.cd(self.name)
        if not git.valid():
            raise self._invalid_repository

        # Check for uncommitted changes
        if not force:
            log.debug("Confirming there are no uncommitted changes...")
            if git.changes(self.type, include_untracked=clean):
                msg = "Uncommitted changes in {}".format(os.getcwd())
                raise exceptions.UncommittedChanges(msg)

        # Fetch the desired revision
        if fetch or git.is_fetch_required(self.type, self.rev):
            git.fetch(self.type, self.repo, self.name, rev=self.rev)

        # Update the working tree to the desired revision
        git.update(self.type, self.repo, self.name,
                   fetch=fetch, clean=clean, rev=self.rev)

    def create_link(self, root, force=False):
        """Create a link from the target name to the current directory."""
        if not self.link:
            return

        log.info("Creating a symbolic link...")

        if os.name == 'nt':
            warnings.warn("Symbolic links are not supported on Windows")
            return

        target = os.path.join(root, self.link)
        source = os.path.relpath(os.getcwd(), os.path.dirname(target))

        if os.path.islink(target):
            os.remove(target)
        elif os.path.exists(target):
            if force:
                shell.rm(target)
            else:
                msg = "Preexisting link location at {}".format(target)
                raise exceptions.UncommittedChanges(msg)

        shell.ln(source, target)

    def run_scripts(self, force=False):
        log.info("Running install scripts...")

        # Enter the working tree
        shell.cd(self.name)
        if not git.valid():
            raise self._invalid_repository

        # Check for scripts
        if not self.scripts:
            common.show("(no scripts to run)", color='shell_info')
            common.newline()
            return

        # Run all scripts
        for script in self.scripts:
            try:
                lines = shell.call(script, _shell=True)
            except exceptions.ShellError as exc:
                common.show(*exc.output, color='shell_error')
                cmd = exc.program
                if force:
                    log.debug("Ignored error from call to '%s'", cmd)
                else:
                    msg = "Command '{}' failed in {}".format(cmd, os.getcwd())
                    raise exceptions.ScriptFailure(msg)
            else:
                common.show(*lines, color='shell_output')
        common.newline()

    def identify(self, allow_dirty=True, allow_missing=True):
        """Get the path and current repository URL and hash."""
        if os.path.isdir(self.name):

            shell.cd(self.name)
            if not git.valid():
                raise self._invalid_repository

            path = os.getcwd()
            url = git.get_url(self.type)
            if git.changes(self.type,
                           display_status=not allow_dirty, _show=True):
                if not allow_dirty:
                    msg = "Uncommitted changes in {}".format(os.getcwd())
                    raise exceptions.UncommittedChanges(msg)

                common.show(self.DIRTY, color='git_dirty', log=False)
                common.newline()
                return path, url, self.DIRTY

            rev = git.get_hash(self.type, _show=True)
            common.show(rev, color='git_rev', log=False)
            common.newline()
            return path, url, rev

        if allow_missing:
            return os.getcwd(), '<missing>', self.UNKNOWN

        raise self._invalid_repository

    def lock(self, rev=None):
        """Return a locked version of the current source."""
        if rev is None:
            _, _, rev = self.identify(allow_dirty=False, allow_missing=False)

        source = self.__class__(self.type, self.repo,
                                self.name, rev,
                                self.link, self.scripts,
                                self.sparse_paths)
        return source

    @property
    def _invalid_repository(self):
        path = os.path.join(os.getcwd(), self.name)
        msg = "Not a valid repository: {}".format(path)
        return exceptions.InvalidRepository(msg)

    @staticmethod
    def _infer_name(repo):
        filename = repo.split('/')[-1]
        name = filename.split('.')[0]
        return name
