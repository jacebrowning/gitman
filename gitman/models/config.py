import os
import sys
from pathlib import Path
from typing import Iterator, List, Optional

import log
from datafiles import datafile, field

from .. import common, exceptions, shell
from ..decorators import preserve_cwd
from .group import Group
from .source import Identity, Source


@datafile("{self.root}/{self.filename}", defaults=True, manual=True)
class Config:
    """Specifies all dependencies for a project."""

    root: Optional[str] = None
    filename: str = "gitman.yml"

    location: str = "gitman_sources"
    sources: List[Source] = field(default_factory=list)
    sources_locked: List[Source] = field(default_factory=list)
    default_group: str = field(default_factory=str)
    groups: List[Group] = field(default_factory=list)

    def __post_init__(self):
        if self.root is None:
            self.root = os.getcwd()

    @property
    def config_path(self) -> str:
        """Get the full path to the config file."""
        assert self.root
        return os.path.normpath(os.path.join(self.root, self.filename))

    path = config_path

    @property
    def log_path(self) -> str:
        """Get the full path to the log file."""
        return os.path.normpath(os.path.join(self.location_path, "gitman.log"))

    @property
    def location_path(self) -> str:
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
                        'group name "{}"'
                    ).format(source.name)
                    raise exceptions.InvalidConfig(msg)

    def get_path(self, name: Optional[str] = None) -> str:
        """Get the full path to a dependency or internal file."""
        base = self.location_path
        if name == "__config__":
            return self.path  # type: ignore
        if name == "__log__":
            return self.log_path
        if name:
            return os.path.normpath(os.path.join(base, name))
        return base

    def install_dependencies(
        self,
        *names: str,
        depth: Optional[int] = None,
        update: bool = True,
        recurse: bool = False,
        force: bool = False,
        force_interactive: bool = False,
        fetch: bool = False,
        clean: bool = True,
        skip_changes: bool = False,
        skip_default_group: bool = False,
    ) -> int:
        """Download or update the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources(use_locked=False if update else None)
        sources_filter = self._get_sources_filter(
            *names, sources=sources, skip_default_group=skip_default_group
        )

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
            assert self.root, f"Missing root: {self}"
            source.create_links(self.root, force=force)
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
                    skip_default_group=skip_default_group,
                )
                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()

        if sources_filter:
            log.error("No such dependency: %s", " ".join(sources_filter))
            return 0

        return count

    @preserve_cwd
    def run_scripts(
        self,
        *names: str,
        depth: Optional[int] = None,
        force: bool = False,
        show_shell_stdout: bool = False,
    ) -> int:
        """Run scripts for the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = self._get_sources()
        sources_filter = self._get_sources_filter(
            *names, sources=sources, skip_default_group=False
        )

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name in sources_filter:
                shell.cd(source.name)

                config = load_config(search=False)
                if config:
                    common.indent()
                    remaining_depth = None if depth is None else max(0, depth - 1)
                    if remaining_depth:
                        common.newline()
                    count += config.run_scripts(depth=remaining_depth, force=force)
                    common.dedent()

                source.run_scripts(force=force, show_shell_stdout=show_shell_stdout)
                count += 1

                shell.cd(self.location_path, _show=False)

        common.dedent()

        return count

    @classmethod
    def _split_name_and_rev(cls, name_rev):
        true_name = name_rev
        rev = None
        if "@" in name_rev:
            name_split = name_rev.split("@")
            true_name = name_split[0]
            rev = name_split[1]
        return true_name, rev

    @classmethod
    def _remap_names_and_revs(cls, names):
        name_rev_map = {}
        for name in names:
            base_name, rev = cls._split_name_and_rev(name)
            name_rev_map[base_name] = rev
        return name_rev_map.keys(), name_rev_map

    def lock_dependencies(
        self, *names: str, obey_existing: bool = True, skip_changes: bool = False
    ) -> int:
        """Lock down the immediate dependency versions."""
        sources_to_install, source_to_install_revs = self._remap_names_and_revs(
            [*names]
        )
        sources = self._get_sources(use_locked=obey_existing).copy()

        skip_default = True
        if len(sources_to_install) == 0:
            skip_default = False

        sources_filter = self._get_sources_filter(
            *sources_to_install, sources=sources, skip_default_group=skip_default
        )

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        count = 0
        for source in sources:
            if source.name not in sources_filter:
                log.info("Skipped dependency: %s", source.name)
                continue

            rev = None
            if source.name in source_to_install_revs.keys():
                rev = source_to_install_revs[source.name]
            source_locked = source.lock(skip_changes=skip_changes, rev=rev)

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

    def get_dependencies(
        self, depth: Optional[int] = None, allow_dirty: bool = True
    ) -> Iterator[Identity]:
        """Yield the path, repository, and hash of each dependency."""
        if not os.path.exists(self.location_path):
            return

        shell.cd(self.location_path)
        common.newline()
        common.indent()

        for source in self._get_sources(use_locked=False):

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

    def log(self, message: str = "", *args):
        """Append a message to the log file."""
        os.makedirs(self.location_path, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as outfile:
            outfile.write(message.format(*args) + "\n")

    def _get_sources(self, *, use_locked: Optional[bool] = None) -> List[Source]:
        """Merge source lists using the requested section as the base."""
        if use_locked is True:
            if self.sources_locked:
                return self.sources_locked
            log.info("No locked sources, defaulting to none")
            return []

        sources: List[Source] = []
        if use_locked is False:
            sources = self.sources
        else:
            if self.sources_locked:
                log.info("Defaulting to locked sources")
                sources = self.sources_locked
            else:
                log.info("No locked sources, using latest")
                sources = self.sources

        extras = []
        for source in self.sources + self.sources_locked:
            if source not in sources:
                log.info("Source %r missing from selected section", source.name)
                extras.append(source)

        return sources + extras

    def _get_sources_filter(
        self, *names: str, sources: List[Source], skip_default_group: bool
    ) -> List[str]:
        """Get a filtered subset of sources."""
        names_list = list(names)
        if not names_list and not skip_default_group:
            names_list.append(self.default_group)

        # Add sources from groups
        groups_filter = [group for group in self.groups if group.name in names_list]
        sources_filter = [member for group in groups_filter for member in group.members]

        # Add independent sources
        sources_filter.extend(
            [source.name for source in sources if source.name in names_list]
        )

        # Fall back to all sources if allowed
        if not sources_filter:
            if names and names_list != ["all"]:
                log.warn(f"No dependencies match: {' '.join(names)}")
            else:
                sources_filter = [source.name for source in sources if source.name]

        return list(set(sources_filter))


def load_config(
    start: Optional[str] = None, *, search: bool = True
) -> Optional[Config]:
    """Load the config for the current project."""
    start = os.path.abspath(start) if start else _resolve_current_directory()

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


def find_nested_configs(
    root: str, depth: Optional[int], skip_paths: List[str]
) -> List[Config]:
    """Find all other projects in the same directory."""
    root = os.path.abspath(root) if root else _resolve_current_directory()
    configs: List[Config] = []

    if depth is not None and depth <= 1:
        return configs

    log.debug(f"Searching for nested project in: {root}")
    for name in os.listdir(root):
        if name[0] in {".", "_", "@"}:
            continue
        if name in {"build", "dist", "node_modules", "venv"}:
            continue
        path = os.path.join(root, name)
        if path in skip_paths:
            continue
        if os.path.isdir(path) and not os.path.islink(path):
            if config := load_config(path, search=False):
                configs.append(config)

            if depth is not None:
                configs.extend(find_nested_configs(path, depth - 1, skip_paths))
            else:
                configs.extend(find_nested_configs(path, depth, skip_paths))

    return configs


def _resolve_current_directory():
    start = os.getcwd()
    if sys.version_info < (3, 8) and os.name == "nt":
        log.warn("Python 3.8+ is required to resolve virtual drives on Windows")
    else:
        start = os.path.realpath(start)
        os.chdir(start)
    return start


def _valid_filename(filename):
    name, ext = os.path.splitext(filename.lower())
    if name.startswith("."):
        name = name[1:]
    return name in {"gitman", "gdm"} and ext in {".yml", ".yaml"}


def filter_nested_configs(configs: List[Config]) -> List[Config]:
    """Filter subdirectories inside of parent config."""
    filtered_configs = []
    for config_a in configs:
        is_nested = False
        for config_b in configs:
            if config_a == config_b:
                continue
            if Path(config_b.location_path) in Path(config_a.location_path).parents:
                is_nested = True
                break
        if not is_nested:
            filtered_configs.append(config_a)

    return filtered_configs
