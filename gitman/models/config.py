"""Wrappers for the dependency configuration files."""

import os
import logging

import yorm
from yorm.types import String, SortedList

from .. import common
from .. import shell
from . import Source

log = logging.getLogger(__name__)


@yorm.attr(location=String)
@yorm.attr(sources=SortedList.of_type(Source))
@yorm.attr(sources_locked=SortedList.of_type(Source))
@yorm.sync("{self.root}/{self.filename}")
class Config:
    """A dictionary of dependency configuration options."""

    def __init__(self, root, filename="gitman.yml", location="gdm_sources"):
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
                     update=True, recurse=False,
                     force=False, fetch=False, clean=True):
        """Get all sources."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        if not os.path.isdir(self.location_path):
            shell.mkdir(self.location_path)
        shell.cd(self.location_path)

        sources = self._get_sources(use_locked=False if update else None)
        dirs = list(names) if names else [source.dir for source in sources]
        common.show()
        common.indent()

        count = 0
        for source in sources:
            if source.dir in dirs:
                dirs.remove(source.dir)
            else:
                log.info("Skipped dependency: %s", source.dir)
                continue

            source.update_files(force=force, fetch=fetch, clean=clean)
            source.create_link(self.root, force=force)
            count += 1

            common.show()

            config = load_config()
            if config:
                common.indent()
                count += config.install_deps(
                    depth=None if depth is None else max(0, depth - 1),
                    update=update and recurse,
                    recurse=recurse,
                    force=force,
                    fetch=fetch,
                    clean=clean,
                )
                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()
        if dirs:
            log.error("No such dependency: %s", ' '.join(dirs))
            return 0

        return count

    def lock_deps(self, *names, obey_existing=True):
        """Lock down the immediate dependency versions."""
        shell.cd(self.location_path)
        common.show()
        common.indent()

        sources = self._get_sources(use_locked=obey_existing).copy()
        dirs = list(names) if names else [source.dir for source in sources]

        count = 0
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
            count += 1

            common.show()

            shell.cd(self.location_path, _show=False)

        if count:
            yorm.update_file(self)
        return count

    def uninstall_deps(self):
        """Remove the sources location."""
        shell.rm(self.location_path)
        common.show()

    def get_deps(self, depth=None, allow_dirty=True):
        """Yield the path, repository URL, and hash of each dependency."""
        if not os.path.exists(self.location_path):
            return

        shell.cd(self.location_path)
        common.show()
        common.indent()

        for source in self.sources:

            if depth == 0:
                log.info("Skipped dependency: %s", source.dir)
                continue

            yield source.identify(allow_dirty=allow_dirty)
            common.show()

            config = load_config()
            if config:
                common.indent()
                yield from config.get_deps(
                    depth=None if depth is None else max(0, depth - 1),
                    allow_dirty=allow_dirty,
                )
                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()

    def _get_sources(self, *, use_locked=None):
        """Merge source lists using requested section as the base."""
        if use_locked is True:
            if self.sources_locked:
                return self.sources_locked
            else:
                log.info("No locked sources, defaulting to none...")
                return []

        sources = []
        if use_locked is False:
            sources = self.sources
        else:
            if self.sources_locked:
                log.info("Defalting to locked sources...")
                sources = self.sources_locked
            else:
                log.info("No locked sources, using latest...")
                sources = self.sources

        extras = []
        for source in self.sources + self.sources_locked:
            if source not in sources:
                log.info("Source %r missing from selected section", source.dir)
                extras.append(source)

        return sources + extras


def load_config(root=None):
    """Load the configuration for the current project."""
    if root is None:
        root = os.getcwd()

    for filename in os.listdir(root):
        if _valid_filename(filename):
            config = Config(root, filename)
            log.debug("Loaded config: %s", config.path)
            return config

    log.debug("No config found in: %s", root)
    return None


def _valid_filename(filename):
    name, ext = os.path.splitext(filename.lower())
    if name.startswith('.'):
        name = name[1:]
    return name in ('gitman', 'gdm') and ext in ('.yml', '.yaml')
