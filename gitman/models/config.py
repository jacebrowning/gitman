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
@yorm.sync("{self.root}/{self.filename}", auto_save=False)
class Config(yorm.ModelMixin):
    """Specifies all dependencies for a project."""

    LOG = "gitman.log"

    def __init__(self, root=None,
                 filename="gitman.yml", location="gitman_sources"):
        super().__init__()
        self.root = root or os.getcwd()
        self.filename = filename
        self.location = location
        self.sources = []
        self.sources_locked = []

    @property
    def config_path(self):
        """Get the full path to the config file."""
        return os.path.normpath(os.path.join(self.root, self.filename))
    path = config_path

    @property
    def log_path(self):
        """Get the full path to the log file."""
        return os.path.normpath(os.path.join(self.location_path, self.LOG))

    @property
    def location_path(self):
        """Get the full path to the dependency storage location."""
        return os.path.normpath(os.path.join(self.root, self.location))

    def get_path(self, name=None):
        """Get the full path to a dependency or internal file."""
        base = self.location_path
        if name == '__config__':
            return self.path
        elif name == '__log__':
            return self.log_path
        elif name:
            return os.path.normpath(os.path.join(base, name))
        else:
            return base

    def install_dependencies(self, *names, depth=None,
                             update=True, recurse=False,
                             force=False, fetch=False, clean=True):
        """Download or update the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources(use_locked=False if update else None)
        sources_filter = list(names) if names else [s.name for s in sources]

        if not os.path.isdir(self.location_path):
            shell.mkdir(self.location_path)
        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name in sources_filter:
                sources_filter.remove(source.name)
            else:
                log.info("Skipped dependency: %s", source.name)
                continue

            source.update_files(force=force, fetch=fetch, clean=clean)
            source.create_link(self.root, force=force)
            common.newline()
            count += 1

            config = load_config(search=False)
            if config:
                common.indent()
                count += config.install_dependencies(
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
        if sources_filter:
            log.error("No such dependency: %s", ' '.join(sources_filter))
            return 0

        return count

    def run_scripts(self, *names, depth=None, force=False):
        """Run scripts for the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources()
        sources_filter = list(names) if names else [s.name for s in sources]

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name in sources_filter:
                source.run_scripts(force=force)
                count += 1

                config = load_config(search=False)
                if config:
                    common.indent()
                    count += config.run_scripts(
                        depth=None if depth is None else max(0, depth - 1),
                        force=force,
                    )
                    common.dedent()

                shell.cd(self.location_path, _show=False)

        common.dedent()

        return count

    def lock_dependencies(self, *names, obey_existing=True):
        """Lock down the immediate dependency versions."""
        sources = self._get_sources(use_locked=obey_existing).copy()
        sources_filter = list(names) if names else [s.name for s in sources]

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name not in sources_filter:
                log.info("Skipped dependency: %s", source.name)
                continue

            try:
                index = self.sources_locked.index(source)
            except ValueError:
                self.sources_locked.append(source.lock())
            else:
                self.sources_locked[index] = source.lock()
            count += 1

            shell.cd(self.location_path, _show=False)

        if count:
            self.save()

        return count

    def uninstall_dependencies(self):
        """Delete the dependency storage location."""
        shell.cd(self.root)
        shell.rm(self.location_path)
        common.newline()

    def get_dependencies(self, depth=None, allow_dirty=True):
        """Yield the path, repository URL, and hash of each dependency."""
        if not os.path.exists(self.location_path):
            return

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        for source in self.sources:

            if depth == 0:
                log.info("Skipped dependency: %s", source.name)
                continue

            yield source.identify(allow_dirty=allow_dirty)

            config = load_config(search=False)
            if config:
                common.indent()
                yield from config.get_dependencies(
                    depth=None if depth is None else max(0, depth - 1),
                    allow_dirty=allow_dirty,
                )
                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()

    def log(self, message="", *args):
        """Append a message to the log file."""
        with open(self.log_path, 'a') as outfile:
            outfile.write(message.format(*args) + '\n')

    def _get_sources(self, *, use_locked=None):
        """Merge source lists using the requested section as the base."""
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
                log.info("Defaulting to locked sources...")
                sources = self.sources_locked
            else:
                log.info("No locked sources, using latest...")
                sources = self.sources

        extras = []
        for source in self.sources + self.sources_locked:
            if source not in sources:
                log.info("Source %r missing from selected section", source.name)
                extras.append(source)

        return sources + extras


def load_config(start=None, *, search=True):
    """Load the config for the current project."""
    if start:
        start = os.path.abspath(start)
    else:
        start = os.getcwd()

    if search:
        log.debug("Searching for config...")

    path = start
    while path != os.path.dirname(path):
        log.debug("Looking for config in: %s", path)

        for filename in os.listdir(path):
            if _valid_filename(filename):
                config = Config(path, filename)
                log.debug("Found config: %s", config.path)
                return config

        if search:
            path = os.path.dirname(path)
        else:
            break

    if search:
        log.debug("No config found starting from: %s", start)
    else:
        log.debug("No config found in: %s", start)

    return None


def _valid_filename(filename):
    name, ext = os.path.splitext(filename.lower())
    if name.startswith('.'):
        name = name[1:]
    return name in ['gitman', 'gdm'] and ext in ['.yml', '.yaml']
