import os
from dataclasses import dataclass, field
from typing import List, Optional

import log

from .. import common, exceptions, git, shell


@dataclass
class Source:
    """A dictionary of `git` and `ln` arguments."""

    name: Optional[str]
    type: str
    repo: str
    sparse_paths: List[str] = field(default_factory=list)
    rev: str = 'master'
    link: Optional[str] = None
    scripts: List[str] = field(default_factory=list)

    DIRTY = '<dirty>'
    UNKNOWN = '<unknown>'

    def __post_init__(self):
        if self.name is None:
            self.name = self._infer_name(self.repo)
        self.type = self.type or 'git'

    def __repr__(self):
        return "<source {}>".format(self)

    def __str__(self):
        pattern = "['{t}'] '{r}' @ '{v}' in '{d}'"
        if self.link:
            pattern += " <- '{s}'"
        return pattern.format(
            t=self.type, r=self.repo, v=self.rev, d=self.name, s=self.link
        )

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name

    def update_files(
        self,
        force=False,
        force_interactive=False,
        fetch=False,
        clean=True,
        skip_changes=False,
    ):
        """Ensure the source matches the specified revision."""
        log.info("Updating source files...")

        # Clone the repository if needed
        assert self.name
        valid_checkout_dir = False
        if os.path.isdir(self.name):
            valid_checkout_dir = len(os.listdir(self.name)) == 0
        else:
            valid_checkout_dir = True

        if valid_checkout_dir:
            git.clone(
                self.type,
                self.repo,
                self.name,
                sparse_paths=self.sparse_paths,
                rev=self.rev,
            )

        # Enter the working tree
        shell.cd(self.name)
        if not git.valid():
            if force:
                git.rebuild(self.type, self.repo)
                fetch = True
            else:
                raise self._invalid_repository

        # Check for uncommitted changes
        if not force:
            log.debug("Confirming there are no uncommitted changes...")
            if skip_changes:
                if git.changes(
                    self.type, include_untracked=clean, display_status=False
                ):
                    common.show(
                        f'Skipped update due to uncommitted changes in {os.getcwd()}',
                        color='git_changes',
                    )
                    return
            elif force_interactive:
                if git.changes(
                    self.type, include_untracked=clean, display_status=False
                ):
                    common.show(
                        f'Uncommitted changes found in {os.getcwd()}',
                        color='git_changes',
                    )

                    while True:
                        yn_input = str(
                            input("Do you want to overwrite? (Y/N)[Y]: ")
                        ).rstrip('\r\n')

                        if yn_input.lower() == "y" or not yn_input:
                            break

                        if yn_input.lower() == "n":
                            common.show(
                                f'Skipped update in {os.getcwd()}', color='git_changes'
                            )
                            return

            else:
                if git.changes(self.type, include_untracked=clean):
                    raise exceptions.UncommittedChanges(
                        f'Uncommitted changes in {os.getcwd()}'
                    )

        # Fetch the desired revision
        if fetch or git.is_fetch_required(self.type, self.rev):
            git.fetch(self.type, self.repo, self.name, rev=self.rev)

        # Update the working tree to the desired revision
        git.update(
            self.type, self.repo, self.name, fetch=fetch, clean=clean, rev=self.rev
        )

    def create_link(self, root, force=False):
        """Create a link from the target name to the current directory."""
        if not self.link:
            return

        log.info("Creating a symbolic link...")

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

    def run_scripts(self, force=False, show_shell_stdout=False):
        log.info("Running install scripts...")

        # Enter the working tree
        shell.cd(self.name)
        if not git.valid():
            raise self._invalid_repository

        # Check for scripts
        if not self.scripts or not self.scripts[0]:
            common.show("(no scripts to run)", color='shell_info')
            common.newline()
            return

        # Run all scripts
        for script in self.scripts:
            try:
                shell.call(script, _shell=True, _stream=show_shell_stdout)
            except exceptions.ShellError as exc:
                if show_shell_stdout:
                    common.show('(script returned an error)', color='shell_error')
                else:
                    common.show(*exc.output, color='shell_error')
                cmd = exc.program
                if force:
                    log.debug("Ignored error from call to '%s'", cmd)
                else:
                    msg = "Command '{}' failed in {}".format(cmd, os.getcwd())
                    raise exceptions.ScriptFailure(msg)
        common.newline()

    def identify(self, allow_dirty=True, allow_missing=True, skip_changes=False):
        """Get the path and current repository URL and hash."""
        assert self.name
        if os.path.isdir(self.name):

            shell.cd(self.name)
            if not git.valid():
                raise self._invalid_repository

            path = os.getcwd()
            url = git.get_url(self.type)
            if git.changes(
                self.type,
                display_status=not allow_dirty and not skip_changes,
                _show=not skip_changes,
            ):

                if allow_dirty:
                    common.show(self.DIRTY, color='git_dirty', log=False)
                    common.newline()
                    return path, url, self.DIRTY

                if skip_changes:
                    msg = ("Skipped lock due to uncommitted changes " "in {}").format(
                        os.getcwd()
                    )
                    common.show(msg, color='git_changes')
                    common.newline()
                    return path, url, self.DIRTY

                msg = "Uncommitted changes in {}".format(os.getcwd())
                raise exceptions.UncommittedChanges(msg)

            rev = git.get_hash(self.type, _show=True)
            common.show(rev, color='git_rev', log=False)
            common.newline()
            return path, url, rev

        if allow_missing:
            return os.getcwd(), '<missing>', self.UNKNOWN

        raise self._invalid_repository

    def lock(self, rev=None, allow_dirty=False, skip_changes=False):
        """Create a locked source object.

        Return a locked version of the current source if not dirty
        otherwise None.
        """

        if rev is None:
            _, _, rev = self.identify(
                allow_dirty=allow_dirty, allow_missing=False, skip_changes=skip_changes
            )

        if rev == self.DIRTY:
            return None

        source = self.__class__(
            type=self.type,
            repo=self.repo,
            name=self.name,
            rev=rev,
            link=self.link,
            scripts=self.scripts,
            sparse_paths=self.sparse_paths,
        )
        return source

    @property
    def _invalid_repository(self):
        assert self.name
        path = os.path.join(os.getcwd(), self.name)
        msg = """

            Not a valid repository: {}
            During install you can rebuild a repo with a missing .git directory using the --force option
            """.format(
            path
        )
        return exceptions.InvalidRepository(msg)

    @staticmethod
    def _infer_name(repo):
        filename = repo.split('/')[-1]
        name = filename.split('.')[0]
        return name
