import os
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List, Optional

import log

from .. import common, exceptions, git, shell

Identity = namedtuple("Identity", ["path", "url", "rev"])


@dataclass
class Link:
    source: str = ""
    target: str = ""


@dataclass
class Source:
    """Represents a repository to clone and options for controlling checkout.

    | Key | Purpose | Required | Default |
    | --- | ------- | -------- | ------- |
    | `repo` | URL of the repository | Yes |
    | `name` | Directory for checkout | Yes | (inferred) |
    | `rev` | SHA, tag, or branch to checkout | Yes | `"main"`|
    | `type` | `"git"` or `"git-svn"` | No | `"git"` |
    | `params` | Additional arguments for `clone` | No | `null` |
    | `sparse_paths` | Controls partial checkout | No | `[]` |
    | `links` | Creates symlinks within a project | No | `[]` |
    | `scripts` | Shell commands to run after checkout | No | `[]` |

    ### Params

    Params are passed directly to the `clone` command to modify behavior such as:

    ```
    # Shallow clone:
    params: --depth=1

    # Include submodules:
    params: --recurse-submodules
    ```

    ### Sparse Paths

    See [using sparse checkouts][using-sparse-checkouts] for more information.

    ### Links

    See [using multiple links][using-multiple-links] for more information.

    ### Scripts

    Scripts can be used to run post-checkout commands such us build steps. For example:

    ```
    repo: "https://github.com/koalaman/shellcheck"
    scripts:
      - brew install cabal-install
      - cabal install
    ```

    """

    repo: str = ""
    name: Optional[str] = None
    rev: str = "main"

    type: str = "git"
    params: Optional[str] = None
    sparse_paths: List[str] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)

    scripts: List[str] = field(default_factory=list)

    DIRTY = "<dirty>"
    UNKNOWN = "<unknown>"

    def __post_init__(self):
        if self.name is None:
            self.name = self.repo.split("/")[-1].split(".")[0]
        else:
            self.name = str(self.name)
        self.type = self.type or "git"

    def __repr__(self):
        return f"<source {self}>"

    def __str__(self):
        return f"{self.repo!r} @ {self.rev!r} in {self.name!r}"

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name

    def clone_params_if_any(self):
        # sanitize params strings by splitting on spaces
        if self.params:
            params_list = []
            for param in self.params.split(" "):
                if len(param) > 0:
                    params_list.append(param)
            return params_list
        return None

    def update_files(
        self,
        force: bool = False,
        force_interactive: bool = False,
        fetch: bool = False,
        clean: bool = True,
        skip_changes: bool = False,
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
                user_params=self.clone_params_if_any(),
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
                        f"Skipped update due to uncommitted changes in {os.getcwd()}",
                        color="git_changes",
                    )
                    return
            elif force_interactive:
                if git.changes(
                    self.type, include_untracked=clean, display_status=False
                ):
                    common.show(
                        f"Uncommitted changes found in {os.getcwd()}",
                        color="git_changes",
                    )

                    while True:
                        response = common.prompt("Do you want to overwrite? (y/n): ")
                        if response == "y":
                            break
                        if response in ("n", ""):
                            common.show(
                                f"Skipped update in {os.getcwd()}", color="git_changes"
                            )
                            return

            else:
                if git.changes(self.type, include_untracked=clean):
                    raise exceptions.UncommittedChanges(
                        f"Uncommitted changes in {os.getcwd()}"
                    )

        # Fetch the desired revision
        if fetch or git.is_fetch_required(self.type, self.rev):
            git.fetch(self.type, self.repo, self.name, rev=self.rev)

        # Update the working tree to the desired revision
        git.update(
            self.type, self.repo, self.name, fetch=fetch, clean=clean, rev=self.rev
        )

    def create_links(self, root: str, *, force: bool = False):
        """Create links from the source to target directory."""
        if not self.links:
            return

        for link in self.links:
            target = os.path.join(root, os.path.normpath(link.target))
            relpath = os.path.relpath(os.getcwd(), os.path.dirname(target))
            source = os.path.join(relpath, os.path.normpath(link.source))
            create_sym_link(source, target, force=force)

    def run_scripts(self, force: bool = False, show_shell_stdout: bool = False):
        log.info("Running install scripts...")

        # Enter the working tree
        if not git.valid():
            raise self._invalid_repository

        # Check for scripts
        if not self.scripts or not self.scripts[0]:
            common.show("(no scripts to run)", color="shell_info")
            common.newline()
            return

        # Run all scripts
        for script in self.scripts:
            try:
                shell.call(script, _shell=True, _stream=show_shell_stdout)
            except exceptions.ShellError as exc:
                if show_shell_stdout:
                    common.show("(script returned an error)", color="shell_error")
                else:
                    common.show(*exc.output, color="shell_error")
                cmd = exc.program
                if force:
                    log.debug("Ignored error from call to '%s'", cmd)
                else:
                    msg = "Command '{}' failed in {}".format(cmd, os.getcwd())
                    raise exceptions.ScriptFailure(msg)
        common.newline()

    def identify(
        self,
        allow_dirty: bool = True,
        allow_missing: bool = True,
        skip_changes: bool = False,
    ) -> Identity:
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
                    common.show(self.DIRTY, color="git_dirty", log=False)
                    common.newline()
                    return Identity(path, url, self.DIRTY)

                if skip_changes:
                    msg = ("Skipped lock due to uncommitted changes " "in {}").format(
                        os.getcwd()
                    )
                    common.show(msg, color="git_changes")
                    common.newline()
                    return Identity(path, url, self.DIRTY)

                msg = "Uncommitted changes in {}".format(os.getcwd())
                raise exceptions.UncommittedChanges(msg)

            rev = git.get_hash(self.type, _show=True)
            common.show(rev, color="git_rev", log=False)
            common.newline()
            return Identity(path, url, rev)

        if allow_missing:
            return Identity(os.getcwd(), "<missing>", self.UNKNOWN)

        raise self._invalid_repository

    def lock(
        self,
        rev: Optional[str] = None,
        allow_dirty: bool = False,
        skip_changes: bool = False,
        verify_rev: bool = True,
    ) -> Optional["Source"]:
        """Create a locked source object.

        Return a locked version of the current source if not dirty
        otherwise None.
        """

        if rev is None:
            _, _, rev = self.identify(
                allow_dirty=allow_dirty, allow_missing=False, skip_changes=skip_changes
            )
        elif verify_rev:
            shell.cd(self.name)
            rev_tmp = rev
            rev = git.get_object_rev(rev)
            if rev is None:
                log.error(f"No commit found for {rev_tmp} in source {self.name}")
                return None

        if rev == self.DIRTY:
            return None

        source = self.__class__(
            type=self.type,
            repo=self.repo,
            name=self.name,
            rev=rev,
            links=self.links,
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


def create_sym_link(source: str, target: str, *, force: bool):
    log.info("Creating a symbolic link...")

    if os.path.islink(target):
        os.remove(target)
    elif os.path.exists(target):
        if force:
            shell.rm(target)
        else:
            msg = "Preexisting link location at {}".format(target)
            raise exceptions.UncommittedChanges(msg)

    shell.ln(source, target)
