"""Wrappers for the dependency configuration files."""

import os
import logging

import yorm

from . import common
from .shell import ShellMixin, GitMixin

logging.getLogger('yorm').setLevel(logging.INFO)
log = common.logger(__name__)


@yorm.map_attr(repo=yorm.standard.String)
@yorm.map_attr(dir=yorm.standard.String)
@yorm.map_attr(rev=yorm.standard.String)
@yorm.map_attr(link=yorm.standard.String)
class Source(yorm.extended.AttributeDictionary, ShellMixin, GitMixin):

    """A dictionary of `git` and `ln` arguments."""

    def __init__(self, repo, dir, rev='master', link=None):  # pylint: disable=W0622
        super().__init__()
        self.repo = repo
        self.dir = dir
        self.rev = rev
        self.link = link
        if not self.repo:
            raise ValueError("'repo' missing on {}".format(repr(self)))
        if not self.dir:
            raise ValueError("'dir' missing on {}".format(repr(self)))

    def __repr__(self):
        return "<source {}>".format(self)

    def __str__(self):
        fmt = "'{r}' @ '{v}' in '{d}'"
        if self.link:
            fmt += " <- '{s}'"
        return fmt.format(r=self.repo, v=self.rev, d=self.dir, s=self.link)

    def update_files(self):
        """Ensure the source matches the specified revision."""
        log.info("updating source files...")

        # Fetch the latest changes and revert the working tree if it exists
        if os.path.exists(self.dir):
            self.cd(self.dir)
            self.git_fetch(self.repo)
            self.git_revert()

        # If it doesn't exist, clone a new one
        else:
            self.git_clone(self.repo, self.dir)
            self.cd(self.dir)

        # Update the working tree to the specified revision
        self.git_update(self.rev)

    def create_link(self, root):
        """Create a link from the target name to the current directory."""
        if self.link:
            log.info("creating a symbolic link...")
            target = os.path.join(root, self.link)
            source = os.path.relpath(os.getcwd(), os.path.dirname(target))
            self.ln(source, target)


@yorm.map_attr(all=Source)
class Sources(yorm.container.List):

    """A list of source dependencies."""


@yorm.map_attr(location=yorm.standard.String)
@yorm.map_attr(sources=Sources)
@yorm.store_instances("{self.root}/{self.filename}")
class Config(ShellMixin):

    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', '.gdm.yaml')

    def __init__(self, root, filename=FILENAMES[0], location='gdm_sources'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []

    @property
    def path(self):
        """Get the full path to the configuration file."""
        return os.path.join(self.root, self.filename)

    def install_deps(self):
        """Get all sources, recursively."""
        path = os.path.join(self.root, self.location)

        if not self.indent:
            print()

        if not os.path.isdir(path):
            self.mkdir(path)
        self.cd(path)
        print()

        count = 0
        for source in self.sources:

            source.indent = self.indent + self.INDENT
            source.update_files()
            source.create_link(self.root)
            count += 1
            print()

            count += install_deps(root=os.getcwd(),
                                  indent=source.indent + self.INDENT)

            self.cd(path, visible=False)

        return count


def install_deps(root, indent=0):
    """Install the dependences listed in the project's configuration file."""
    for filename in os.listdir(root):
        if filename.lower() in Config.FILENAMES:
            config = Config(root, filename)
            log.debug("loaded config: %s", config.path)
            config.indent = indent
            return config.install_deps()
    return 0
