# pylint: disable=unused-variable,expression-not-assigned

from unittest.mock import Mock, patch

import log
import pytest
from expecter import expect

from gitman import cli
from gitman.common import _Config
from gitman.exceptions import ScriptFailure, UncommittedChanges


class TestMain:
    """Unit tests for the top-level arguments."""

    def test_main(self):
        """Verify the top-level command can be run."""
        mock_function = Mock(return_value=True)

        cli.main([], mock_function)

        mock_function.assert_called_once_with()

    def test_main_fail(self):
        """Verify error in commands are detected."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(return_value=False))

    def test_main_help(self):
        """Verify the help text can be displayed."""
        with pytest.raises(SystemExit):
            cli.main(["--help"])

    def test_main_none(self):
        """Verify it's an error to specify no command."""
        with pytest.raises(SystemExit):
            cli.main([])

    def test_main_interrupt(self):
        """Verify a command can be interrupted."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=KeyboardInterrupt))

    def test_main_error(self):
        """Verify runtime errors are handled."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=UncommittedChanges))
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=ScriptFailure))


class TestInit:
    """Unit tests for the `init` command."""

    @patch("gitman.commands.init")
    def test_install(self, mock_init):
        """Verify the 'install' command can be run."""
        cli.main(["init"])

        mock_init.assert_called_once_with(force=False)


class TestInstall:
    """Unit tests for the `install` command."""

    @patch("gitman.commands.install")
    def test_install(self, mock_install):
        """Verify the 'install' command can be run."""
        cli.main(["install"])

        mock_install.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            fetch=False,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_root(self, mock_install):
        """Verify the project's root can be specified."""
        cli.main(["install", "--root", "mock/path/to/root"])

        mock_install.assert_called_once_with(
            root="mock/path/to/root",
            depth=5,
            force=False,
            force_interactive=False,
            fetch=False,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_force(self, mock_install):
        """Verify dependencies can be force-installed."""
        cli.main(["install", "--force"])

        mock_install.assert_called_once_with(
            root=None,
            depth=5,
            force=True,
            force_interactive=False,
            fetch=False,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_fetch(self, mock_install):
        """Verify fetching can be enabled."""
        cli.main(["install", "--fetch"])

        mock_install.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            fetch=True,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_clean(self, mock_install):
        """Verify dependency cleaning can be enabled."""
        cli.main(["install", "--clean"])

        mock_install.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            fetch=False,
            clean=True,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_specific_sources(self, mock_install):
        """Verify individual dependencies can be installed."""
        cli.main(["install", "foo", "bar"])

        mock_install.assert_called_once_with(
            "foo",
            "bar",
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            fetch=False,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install")
    def test_install_with_depth(self, mock_update):
        """Verify the 'install' command can be limited by depth."""
        cli.main(["install", "--depth", "10"])

        mock_update.assert_called_once_with(
            root=None,
            depth=10,
            force=False,
            force_interactive=False,
            fetch=False,
            clean=False,
            skip_changes=False,
            skip_scripts=False,
            skip_default_group=False,
        )

    @patch("gitman.commands.install", Mock())
    def test_install_with_depth_invalid(self):
        """Verify depths below 1 are rejected."""
        with pytest.raises(SystemExit):
            cli.main(["install", "--depth", "0"])
        with pytest.raises(SystemExit):
            cli.main(["install", "--depth", "-1"])


class TestUpdate:
    """Unit tests for the `update` command."""

    @patch("gitman.commands.update")
    def test_update(self, mock_update):
        """Verify the 'update' command can be run."""
        cli.main(["update"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_recursive(self, mock_update):
        """Verify the 'update' command can be run recursively."""
        cli.main(["update", "--all"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=True,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_no_lock(self, mock_update):
        """Verify the 'update' command can disable locking."""
        cli.main(["update", "--skip-lock"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=False,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_skip_changes(self, mock_update):
        """Verify the 'update' command with skip changes option."""
        cli.main(["update", "--skip-changes"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=True,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_force(self, mock_update):
        """Verify the 'update' command with force option."""
        cli.main(["update", "--force"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=True,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_force_interactive(self, mock_update):
        """Verify the 'update' command with force-interactive option."""
        cli.main(["update", "--force-interactive"])

        mock_update.assert_called_once_with(
            root=None,
            depth=5,
            force=False,
            force_interactive=True,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_specific_sources(self, mock_install):
        """Verify individual dependencies can be installed."""
        cli.main(["update", "foo", "bar"])

        mock_install.assert_called_once_with(
            "foo",
            "bar",
            root=None,
            depth=5,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )

    @patch("gitman.commands.update")
    def test_update_with_depth(self, mock_update):
        """Verify the 'update' command can be limited by depth."""
        cli.main(["update", "--depth", "10"])

        mock_update.assert_called_once_with(
            root=None,
            depth=10,
            force=False,
            force_interactive=False,
            clean=False,
            recurse=False,
            lock=None,
            skip_changes=False,
            skip_scripts=False,
        )


class TestList:
    """Unit tests for the `list` command."""

    @patch("gitman.commands.display")
    def test_list(self, mock_display):
        """Verify the 'list' command can be run."""
        cli.main(["list"])

        mock_display.assert_called_once_with(root=None, depth=5, allow_dirty=True)

    @patch("gitman.commands.display")
    def test_list_root(self, mock_display):
        """Verify the project's root can be specified."""
        cli.main(["list", "--root", "mock/path/to/root"])

        mock_display.assert_called_once_with(
            root="mock/path/to/root", depth=5, allow_dirty=True
        )

    @patch("gitman.commands.display")
    def test_list_no_dirty(self, mock_display):
        """Verify the 'list' command can be set to fail when dirty."""
        cli.main(["list", "--fail-if-dirty"])

        mock_display.assert_called_once_with(root=None, depth=5, allow_dirty=False)

    @patch("gitman.commands.display")
    def test_update_with_depth(self, mock_update):
        """Verify the 'list' command can be limited by depth."""
        cli.main(["list", "--depth", "10"])

        mock_update.assert_called_once_with(root=None, depth=10, allow_dirty=True)


def describe_lock():
    @patch("gitman.commands.lock")
    def with_no_arguments(lock):
        cli.main(["lock"])
        lock.assert_called_once_with(root=None, depth=5)

    @patch("gitman.commands.lock")
    def with_dependencies(lock):
        cli.main(["lock", "foo", "bar"])
        lock.assert_called_once_with("foo", "bar", root=None, depth=5)


class TestUninstall:
    """Unit tests for the `uninstall` command."""

    @patch("gitman.commands.delete")
    def test_uninstall(self, mock_uninstall):
        """Verify the 'uninstall' command can be run."""
        cli.main(["uninstall"])

        mock_uninstall.assert_called_once_with(
            root=None, force=False, keep_location=False
        )

    @patch("gitman.commands.delete")
    def test_uninstall_root(self, mock_uninstall):
        """Verify the project's root can be specified."""
        cli.main(["uninstall", "--root", "mock/path/to/root"])

        mock_uninstall.assert_called_once_with(
            root="mock/path/to/root", force=False, keep_location=False
        )

    @patch("gitman.commands.delete")
    def test_uninstall_force(self, mock_uninstall):
        """Verify the 'uninstall' command can be forced."""
        cli.main(["uninstall", "--force"])

        mock_uninstall.assert_called_once_with(
            root=None, force=True, keep_location=False
        )

    @patch("gitman.commands.delete")
    def test_uninstall_keep_location(self, mock_uninstall):
        """Verify the 'uninstall' command can be run with keep_location."""
        cli.main(["uninstall", "--keep-location"])

        mock_uninstall.assert_called_once_with(
            root=None, force=False, keep_location=True
        )


def describe_show():
    @patch("gitman.commands.show")
    def with_no_arguments(show):
        cli.main(["show"])
        show.assert_called_once_with(root=None)

    @patch("gitman.commands.show")
    def with_root(show):
        cli.main(["show", "--root", "mock/root"])
        show.assert_called_once_with(root="mock/root")

    @patch("gitman.commands.show")
    def with_names(show):
        cli.main(["show", "foo", "bar"])
        show.assert_called_once_with("foo", "bar", root=None)

    @patch("gitman.commands.show")
    def with_config(show):
        cli.main(["show", "--config"])
        show.assert_called_once_with("__config__", root=None)

    @patch("gitman.commands.show")
    def with_log(show):
        cli.main(["show", "--log"])
        show.assert_called_once_with("__log__", root=None)


def describe_edit():
    @patch("gitman.commands.edit")
    def with_no_arguments(edit):
        cli.main(["edit"])
        edit.assert_called_once_with(root=None)

    @patch("gitman.commands.edit")
    def with_root(edit):
        cli.main(["edit", "--root", "mock/root"])
        edit.assert_called_once_with(root="mock/root")


def describe_logging():

    argument_verbosity = [
        (None, 0),
        ("-v", 1),
        ("-vv", 2),
        ("-vvv", 3),
        ("-vvvv", 4),
        ("-vvvvv", 4),
        ("-q", -1),
    ]

    @pytest.mark.parametrize("argument,verbosity", argument_verbosity)
    def at_each_level(argument, verbosity):
        def function(*args, **kwargs):
            log.debug(args)
            log.debug(kwargs)
            log.warning("warning")
            log.error("error")
            return True

        cli.main([argument] if argument else [], function)
        expect(_Config.verbosity) == verbosity
