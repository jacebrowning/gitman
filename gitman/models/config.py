import os
from typing import List, Optional

import log
from datafiles import datafile, field

from .. import common, exceptions, shell
from .group import Group
from .source import Source


@datafile("{self.root}/{self.filename}", defaults=True, manual=True)
class Config:
    """Specifies all dependencies for a project."""

    root: Optional[str] = None
    filename: str = "gitman.yml"

    location: str = "gitman_sources"
    sources: List[Source] = field(default_factory=list)
    sources_locked: List[Source] = field(default_factory=list)
    groups: List[Group] = field(default_factory=list)

    def __post_init__(self):
        if self.root is None:
            self.root = os.getcwd()

    @property
    def config_path(self):
        """Get the full path to the config file."""
        assert self.root
        return os.path.normpath(os.path.join(self.root, self.filename))

    path = config_path

    @property
    def log_path(self):
        """Get the full path to the log file."""
        return os.path.normpath(os.path.join(self.location_path, "gitman.log"))

    @property
    def location_path(self):
        """Get the full path to the dependency storage location."""
        assert self.root
        return os.path.normpath(os.path.join(self.root, self.location))

    def validate(self):
        """Check for conflicts between source names and group names."""
        for source in self.sources:
            for group in self.groups:
                if source.name == group.name:
                    msg = (
                        "Name conflict detected between source name and "
                        "group name \"{}\""
                    ).format(source.name)
                    raise exceptions.InvalidConfig(msg)

    def get_path(self, name=None):
        """Get the full path to a dependency or internal file."""
        base = self.location_path
        if name == '__config__':
            return self.path
        if name == '__log__':
            return self.log_path
        if name:
            return os.path.normpath(os.path.join(base, name))
        return base

    def install_dependencies(
        self,
        *names,
        depth=None,
        update=True,
        recurse=False,
        force=False,
        force_interactive=False,
        fetch=False,
        clean=True,
        skip_changes=False,
    ):  # pylint: disable=too-many-locals
        """Download or update the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources(use_locked=False if update else None)
        sources_filter = self._get_sources_filter(*names, sources=sources)

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

            source.update_files(
                force=force,
                force_interactive=force_interactive,
                fetch=fetch,
                clean=clean,
                skip_changes=skip_changes,
            )
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
                    skip_changes=skip_changes,
                )
                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()
        if sources_filter:
            log.error("No such dependency: %s", ' '.join(sources_filter))
            return 0

        return count

    def run_scripts(self, *names, depth=None, force=False, show_shell_stdout=False):
        """Run scripts for the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources()
        sources_filter = self._get_sources_filter(*names, sources=sources)

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name in sources_filter:
                source.run_scripts(force=force, show_shell_stdout=show_shell_stdout)
                count += 1

                config = load_config(search=False)
                if config:
                    common.indent()
                    count += config.run_scripts(
                        depth=None if depth is None else max(0, depth - 1), force=force
                    )
                    common.dedent()

                shell.cd(self.location_path, _show=False)

        common.dedent()

        return count

    def lock_dependencies(self, *names, obey_existing=True, skip_changes=False):
        """Lock down the immediate dependency versions."""
        sources = self._get_sources(use_locked=obey_existing).copy()
        sources_filter = self._get_sources_filter(*names, sources=sources)

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name not in sources_filter:
                log.info("Skipped dependency: %s", source.name)
                continue

            source_locked = source.lock(skip_changes=skip_changes)

            if source_locked is not None:
                try:
                    index = self.sources_locked.index(source)
                except ValueError:
                    self.sources_locked.append(source_locked)
                else:
                    self.sources_locked[index] = source_locked
                count += 1

            shell.cd(self.location_path, _show=False)

        if count:
            self.datafile.save()

        common.dedent()

        return count

    def uninstall_dependencies(self):
        """Delete the dependency storage location."""
        shell.cd(self.root)
        shell.rm(self.location_path)
        common.newline()

    def clean_dependencies(self):
        """Delete the dependency storage location."""
        for path in self.get_top_level_dependencies():

            if path == self.location_path:
                log.info("Skipped dependency: %s", path)
            else:
                shell.rm(path)

            common.newline()

        shell.rm(self.log_path)

    def get_top_level_dependencies(self):
        """Yield the path, repository, and hash of top-level dependencies."""
        if not os.path.exists(self.location_path):
            return

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        for source in self.sources:

            assert source.name
            yield os.path.join(self.location_path, source.name)

            shell.cd(self.location_path, _show=False)

        common.dedent()

    def get_dependencies(self, depth=None, allow_dirty=True):
        """Yield the path, repository, and hash of each dependency."""
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
            log.info("No locked sources, defaulting to none...")
            return []

        sources: List[Source] = []
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

    def _get_sources_filter(self, *names, sources):
        """Get filtered sublist of sources."""
        sources_filter = None

        groups_filter = [group for group in self.groups if group.name in list(names)]

        if groups_filter:
            sources_filter = [
                members for group in groups_filter for members in group.members
            ]
        else:
            sources_filter = list(names) if names else [s.name for s in sources]

        return sources_filter


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
                config.validate()
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
    return name in {'gitman', 'gdm'} and ext in {'.yml', '.yaml'}
