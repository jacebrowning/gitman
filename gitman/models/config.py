import os
import sys
from typing import List, Optional

import log
from datafiles import datafile, field

from .. import common, exceptions, shell
from ..decorators import preserve_cwd
from .group import Group
from .source import Source, create_sym_link


# TODO remove the next pylint statement and adapt code

# disable because of the dynamics setattr in __post_init__ to avoid
# that datafile persist this values -> is there another way to tell
# datafiles to ignore specified fiels
# pylint: disable=attribute-defined-outside-init, access-member-before-definition

# due to the protected access of _get_sources -> make them public in the next step
# pylint: disable=protected-access


@datafile("{self.root}/{self.filename}", defaults=True, manual=True)
class Config:
    RESOLVER_RECURSIVE_NESTED = "recursive-nested"
    RESOLVER_RECURSIVE_FLAT = "recursive-flat"
    RESOLVER_RECURSIVE_FLAT_NESTED_LINKS = "recursive-flat-nested-links"
    RESOLVER_FLAT = "flat"

    """Specifies all dependencies for a project."""

    root: Optional[str] = None
    filename: str = "gitman.yml"
    location: str = "gitman_sources"
    resolver: str = RESOLVER_RECURSIVE_NESTED
    sources: List[Source] = field(default_factory=list)
    sources_locked: List[Source] = field(default_factory=list)
    default_group: str = field(default_factory=str)
    groups: List[Group] = field(default_factory=list)

    def __post_init__(self):
        if self.root is None:
            self.root = os.getcwd()

        # used only internally and should not be serialized
        location_path = os.path.normpath(os.path.join(self.root, self.location))
        setattr(self, 'location_path', location_path)
        processed_sources: List[Source] = []
        setattr(self, 'processed_sources', processed_sources)
        registered_sources: List[Source] = []
        setattr(self, 'registered_sources', registered_sources)

        # check if any of the valid resolver values is set
        # if not then set RESOLVER_RECURSIVE_NESTED as default
        if (
            self.resolver != Config.RESOLVER_RECURSIVE_NESTED
            and self.resolver != Config.RESOLVER_RECURSIVE_FLAT
            and self.resolver != Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS
            and self.resolver != Config.RESOLVER_FLAT
        ):
            msg = "Unknown resolver name \"{}\"".format(self.resolver)
            raise exceptions.InvalidConfig(msg)

    def __post_load__(self):
        # update location path because default location may different then loaded value
        self.location_path = os.path.normpath(
            os.path.join(self.root, self.location)  # type: ignore[arg-type]
        )

    @property
    def config_path(self) -> str:
        """Get the full path to the config file."""
        assert self.root
        return os.path.normpath(
            os.path.join(self.root, self.filename)  # type: ignore[arg-type]
        )

    path = config_path

    @property
    def log_path(self) -> str:
        """Get the full path to the log file."""
        return os.path.normpath(os.path.join(self.location_path, "gitman.log"))

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
        skip_default_group=False,
    ):  # pylint: disable=too-many-locals, too-many-statements
        """Download or update the specified dependencies."""
        if depth == 0:
            log.info("Skipped directory: %s", self.location_path)
            return 0

        sources = None
        sources_filter = None

        if (  # pylint: disable=too-many-nested-blocks
            self.resolver == Config.RESOLVER_RECURSIVE_FLAT
            or self.resolver == Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS
        ):
            sources = self._get_sources(
                use_locked=False if update else None, use_extra=False
            )
            sources_filter = self._get_sources_filter(
                *names, sources=sources, skip_default_group=skip_default_group
            )

            # gather flat sources and check for rev conflicts
            new_sources: List[Source] = []
            for source in sources:
                add_source: bool = True
                for registered_source in self.registered_sources:  # type: ignore
                    if (
                        source.name == registered_source.name
                    ):  # check if current source was already processed
                        if (
                            source.rev != registered_source.rev
                            or source.repo != registered_source.repo
                        ):
                            # we skip the detected recursed branch rev if we install
                            # locked sources always the toplevel rev is leading and
                            # to ensure creation order we process the locked version
                            # next instead of the noted rev
                            if not update:
                                # check if we have already processed the matched source
                                # pylint: disable=line-too-long
                                if not registered_source in self.processed_sources:  # type: ignore
                                    new_sources.append(registered_source)
                                else:
                                    # already processed therefore we don't care anymore
                                    sources_filter.remove(source.name)

                                add_source = False
                                continue

                            error_msg = (
                                "Repo/rev conflict encountered in "
                                "flat hierarchy while updating {}\n"
                                "Details: {} conflict with {}"
                            ).format(self.root, str(registered_source), str(source))
                            raise exceptions.InvalidConfig(error_msg)

                # new source name detected -> store new source name
                # to list (cache) used to check for rev conflicts
                if add_source:
                    self.registered_sources.append(source)  # type: ignore
                    new_sources.append(source)

            # assign filtered and collected sources
            sources = new_sources

        else:
            sources = self._get_sources(use_locked=False if update else None)
            sources_filter = self._get_sources_filter(
                *names, sources=sources, skip_default_group=skip_default_group
            )

            for source in sources:
                for registered_source in self.registered_sources:  # type: ignore
                    if (
                        source.name == registered_source.name
                    ):  # check if current source was already processed
                        error_msg = (
                            "Repo conflict encountered "
                            "while updating {}\n"
                            "Details: {} conflict with {}"
                        ).format(self.root, str(registered_source), str(source))
                        raise exceptions.InvalidConfig(error_msg)

                self.registered_sources.append(source)  # type: ignore

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

            # check if source has not already been processed
            if source in self.processed_sources:  # type: ignore
                continue

            source.update_files(
                force=force,
                force_interactive=force_interactive,
                fetch=fetch,
                clean=clean,
                skip_changes=skip_changes,
            )
            source.create_links(self.root, force=force)

            # store processed source
            self.processed_sources.append(source)  # type: ignore

            common.newline()
            count += 1

            if self.resolver == Config.RESOLVER_FLAT:
                # don't process nested configs if flat resolver is active
                continue

            config = load_config(search=False)
            if config:
                common.indent()

                if (
                    self.resolver == Config.RESOLVER_RECURSIVE_FLAT
                    or self.resolver == Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS
                ):
                    # Top level preference for flat hierarchy should
                    # forward / propagate resolver settings
                    config.resolver = self.resolver
                    # forward / override default location -> always use root location
                    # to install dependencies all into the same folder
                    org_location_path = config.location_path
                    config.location_path = self.location_path
                    # forward registered and processed sources list to
                    # check for global conflicts
                    config.registered_sources = self.registered_sources  # type: ignore
                    config.processed_sources = self.processed_sources  # type: ignore

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

                # create nested symlinks
                if self.resolver == Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS:
                    for src in config.sources:
                        link_src = os.path.join(self.location_path, src.name)
                        link_target = os.path.join(org_location_path, src.name)
                        create_sym_link(link_src, link_target, True)

                common.dedent()

            shell.cd(self.location_path, _show=False)

        common.dedent()
        if sources_filter:
            log.error("No such dependency: %s", ' '.join(sources_filter))
            return 0

        return count

    @preserve_cwd
    def run_scripts(self, *names, depth=None, force=False, show_shell_stdout=False):
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

                if self.resolver == Config.RESOLVER_FLAT:
                    # don't process nested configs if flat resolver is active
                    continue

                config = load_config(search=False)
                if config:
                    common.indent()
                    remaining_depth = None if depth is None else max(0, depth - 1)
                    if remaining_depth:
                        common.newline()

                    if (
                        self.resolver == Config.RESOLVER_RECURSIVE_FLAT
                        or self.resolver == Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS
                    ):
                        # Top level preference for flat hierarchy should
                        # always propagate resolver settings
                        config.resolver = self.resolver
                        # override default location -> always use root location
                        # to install dependencies all into the same folder
                        config.location_path = self.location_path
                        # forward processed sources list to check for global conflicts
                        # pylint: disable=line-too-long
                        config.processed_sources = self.processed_sources  # type: ignore

                    count += config.run_scripts(depth=remaining_depth, force=force)
                    common.dedent()

                source.run_scripts(force=force, show_shell_stdout=show_shell_stdout)
                count += 1

                shell.cd(self.location_path, _show=False)

        common.dedent()

        return count

    def lock_dependencies(self, *names, obey_existing=True, skip_changes=False):
        """Lock down the immediate dependency versions."""
        recursive = (
            self.resolver == Config.RESOLVER_RECURSIVE_FLAT
            or self.resolver == Config.RESOLVER_RECURSIVE_FLAT_NESTED_LINKS
        )
        sources = self._get_sources(
            use_locked=obey_existing, recursive=recursive
        ).copy()
        sources_filter = self._get_sources_filter(
            *names, sources=sources, skip_default_group=False
        )

        if not os.path.isdir(self.location_path):
            raise exceptions.InvalidRepository("No dependencies resolved")

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
        os.makedirs(self.location_path, exist_ok=True)
        with open(self.log_path, 'a') as outfile:
            outfile.write(message.format(*args) + '\n')

    def _get_sources(self, *, use_locked=None, use_extra=True, recursive=False):
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

        if recursive:
            recursive_sources = sources
            for source in sources:
                config_path = os.path.join(
                    self.location_path, source.name  # type: ignore[arg-type]
                )
                config = load_config(start=config_path, search=False)
                if config:
                    recursive_sources = recursive_sources + config._get_sources(
                        use_locked=use_locked, use_extra=False, recursive=True
                    )

            for source in recursive_sources:
                if source not in sources:
                    extras.append(source)

        if use_extra:
            all_sources = self.sources + self.sources_locked
            for source in all_sources:
                if source not in sources:
                    log.info("Source %r missing from selected section", source.name)
                    extras.append(source)

        return sources + extras

    def _get_sources_filter(self, *names, sources, skip_default_group):
        """Get filtered sublist of sources."""
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

        if not sources_filter:
            sources_filter = [source.name for source in sources]

        return list(set(sources_filter))


def load_config(start=None, *, search=True):
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
                config.__post_load__()
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
    if name.startswith('.'):
        name = name[1:]
    return name in {'gitman', 'gdm'} and ext in {'.yml', '.yaml'}
