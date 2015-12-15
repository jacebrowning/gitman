"""Wrappers for the dependency configuration files."""

import os
import logging

import yorm

from . import common
from .shell import ShellMixin, GitMixin

log = logging.getLogger(__name__)


@yorm.attr(repo=yorm.converters.String)
@yorm.attr(dir=yorm.converters.String)
@yorm.attr(rev=yorm.converters.String)
@yorm.attr(link=yorm.converters.String)
class Source(yorm.converters.AttributeDictionary, ShellMixin, GitMixin):
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

    def __eq__(self, other):
        return self.dir == other.dir

    def __ne__(self, other):
        return self.dir != other.dir

    def __lt__(self, other):
        return self.dir < other.dir

    def update_files(self, force=False, clean=True):
        """Ensure the source matches the specified revision."""
        log.info("Updating source files...")

        # Enter the working tree
        if not os.path.exists(self.dir):
            log.debug("Creating a new repository...")
            self.git_clone(self.repo, self.dir)
        self.cd(self.dir)

        # Check for uncommitted changes
        if not force:
            log.debug("Confirming there are no uncommitted changes...")
            if self.git_changes():
                common.show()
                msg = "Uncommitted changes: {}".format(os.getcwd())
                raise RuntimeError(msg)

        # Fetch the desired revision
        self.git_fetch(self.repo, self.rev)

        # Update the working tree to the desired revision
        self.git_update(self.rev, clean=clean)

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
                    self.rm(target)
                else:
                    common.show()
                    msg = "Preexisting link location: {}".format(target)
                    raise RuntimeError(msg)
            self.ln(source, target)

    def identify(self, allow_dirty=True):
        """Get the path and current repository URL and hash."""
        if os.path.isdir(self.dir):

            self.cd(self.dir)

            path = os.getcwd()
            url = self.git_get_url()
            if self.git_changes(visible=True):
                revision = '<dirty>'
                if not allow_dirty:
                    common.show()
                    msg = "Uncommitted changes: {}".format(os.getcwd())
                    raise RuntimeError(msg)
            else:
                revision = self.git_get_sha()
            common.show(revision, log=False)

            return path, url, revision

        else:

            return os.getcwd(), '<missing>', '<unknown>'

    def lock(self):
        """Return a locked version of the current source."""
        _, _, sha = self.identify()
        source = self.__class__(self.repo, self.dir, sha, self.link)
        return source


@yorm.attr(all=Source)
class Sources(yorm.converters.SortedList):
    """A list of source dependencies."""


@yorm.attr(location=yorm.converters.String)
@yorm.attr(sources=Sources)
@yorm.attr(sources_locked=Sources)
@yorm.sync("{self.root}/{self.filename}")
class Config(ShellMixin):
    """A dictionary of dependency configuration options."""

    FILENAMES = ('gdm.yml', 'gdm.yaml', '.gdm.yml', '.gdm.yaml')

    def __init__(self, root, filename=FILENAMES[0], location='gdm_sources'):
        super().__init__()
        self.root = root
        self.filename = filename
        self.location = location
        self.sources = []
        self.sources_locked = []

    @property
    def path(self):
        """Get the full path to the configuration file."""
        return os.path.join(self.root, self.filename)

    @property
    def location_path(self):
        """Get the full path to the sources location."""
        return os.path.join(self.root, self.location)

    def install_deps(self, *names, depth=None,
                     update=True, recurse=False, force=False, clean=True):
        """Get all sources."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        if not os.path.isdir(self.location_path):
            self.mkdir(self.location_path)
        self.cd(self.location_path)

        sources = self._get_sources(update)
        dirs = list(names) if names else [source.dir for source in sources]
        common.show()
        common.indent()

        count = 0
        for source in sources:
            if source.dir in dirs:
                dirs.remove(source.dir)
                count += 1
            else:
                log.info("Skipped dependency: %s", source.dir)
                continue

            source.update_files(force=force, clean=clean)
            source.create_link(self.root, force=force)
            common.show()

            config = load()
            if config:
                common.indent()
                count += config.install_deps(
                    depth=None if depth is None else max(0, depth - 1),
                    update=update and recurse,
                    recurse=recurse,
                    force=force,
                    clean=clean,
                )
                common.dedent()

            self.cd(self.location_path, visible=False)

        common.dedent()
        if dirs:
            log.error("No such dependency: %s", ' '.join(dirs))
            return 0

        return count

    def lock_deps(self, *names):
        """Lock down the immediate dependency versions."""
        self.cd(self.location_path)
        common.show()
        common.indent()

        sources = self.sources_locked.copy()
        dirs = list(names) if names else [source.dir for source in sources]

        for source in sources:
            if source.dir not in dirs:
                log.info("Skipped dependency: %s", source.dir)
                continue

            try:
                index = self.sources_locked.index(source)
            except ValueError:
                self.sources_locked.append(source.lock())
            else:
                self.sources_locked[index] = source.lock()

            common.show()

            self.cd(self.location_path, visible=False)

    def uninstall_deps(self):
        """Remove the sources location."""
        self.rm(self.location_path)
        common.show()

    def get_deps(self, depth=None, allow_dirty=True):
        """Yield the path, repository URL, and hash of each dependency."""
        if os.path.exists(self.location_path):
            self.cd(self.location_path)
            common.show()
            common.indent()
        else:
            return

        for source in self.sources:

            if depth == 0:
                log.info("Skipped dependency: %s", source.dir)
                continue

            yield source.identify(allow_dirty=allow_dirty)
            common.show()

            config = load()
            if config:
                common.indent()
                yield from config.get_deps(
                    depth=None if depth is None else max(0, depth - 1),
                    allow_dirty=allow_dirty,
                )
                common.dedent()

            self.cd(self.location_path, visible=False)

        common.dedent()

    def _get_sources(self, update):
        if update:
            return self.sources
        elif self.sources_locked:
            return self.sources_locked
        else:
            log.info("No locked sources available, installing latest...")
            return self.sources


def load(root=None):
    """Load the configuration for the current project."""
    if root is None:
        root = os.getcwd()

    for filename in os.listdir(root):
        if filename.lower() in Config.FILENAMES:
            config = Config(root, filename)
            log.debug("Loaded config: %s", config.path)
            return config

    log.debug("No config found in: %s", root)
    return None
