"""Unit tests for the 'cli' module."""
# pylint: disable=no-self-use

import pytest
from unittest.mock import Mock, patch
import logging

from gdm import cli
from gdm import common


class TestMain:

    """Unit tests for the top-level arguments."""

    def test_main(self):
        """Verify the top-level command can be run."""
        mock_function = Mock(return_value=True)
        cli.main([], mock_function)
        mock_function.assert_called_once_with(root=None)

    def test_main_fail(self):
        """Verify error in commands are detected."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(return_value=False))

    def test_main_help(self):
        """Verify the help text can be displayed."""
        with pytest.raises(SystemExit):
            cli.main(['--help'])

    def test_main_none(self):
        """Verify it's an error to specify no command."""
        with pytest.raises(SystemExit):
            cli.main([])

    def test_main_interrupt(self):
        """Verify a command can be interrupted."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=KeyboardInterrupt))

    @patch('gdm.cli.log')
    def test_main_interrupt_verbose(self, mock_log):
        """Verify a command can be interrupted (verbose output)."""
        with pytest.raises(SystemExit):
            cli.main(['-vvvv'], Mock(side_effect=KeyboardInterrupt))
        assert mock_log.exception.call_count == 1

    def test_main_error(self):
        """Verify runtime errors are handled."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=RuntimeError))


class TestInstallAndUpdate:

    """Unit tests for the `install` and `update` commands."""

    @patch('gdm.commands.install')
    def test_install(self, mock_install):
        """Verify the 'install' command can be run."""
        cli.main(['install'])
        mock_install.assert_called_once_with(root=None,
                                             force=False, clean=False)

    @patch('gdm.commands.install')
    def test_install_root(self, mock_install):
        """Verify the project's root can be specified."""
        cli.main(['install', '--root', 'mock/path/to/root'])
        mock_install.assert_called_once_with(root='mock/path/to/root',
                                             force=False, clean=False)

    @patch('gdm.commands.install')
    def test_install_force(self, mock_install):
        """Verify dependencies can be force-installed."""
        cli.main(['install', '--force'])
        mock_install.assert_called_once_with(root=None,
                                             force=True, clean=False)

    @patch('gdm.commands.install')
    def test_install_clean(self, mock_install):
        """Verify dependency cleaning can be enabled."""
        cli.main(['install', '--clean'])
        mock_install.assert_called_once_with(root=None,
                                             force=False, clean=True)

    @patch('gdm.commands.update')
    def test_update(self, mock_update):
        """Verify the 'update' command can be run."""
        cli.main(['update'])
        mock_update.assert_called_once_with(root=None,
                                            force=False, clean=False)


class TestUninstall:

    """Unit tests for the `uninstall` command."""

    @patch('gdm.commands.delete')
    def test_uninstall(self, mock_uninstall):
        """Verify the 'uninstall' command can be run."""
        cli.main(['uninstall'])
        mock_uninstall.assert_called_once_with(root=None, force=False)

    @patch('gdm.commands.delete')
    def test_uninstall_root(self, mock_uninstall):
        """Verify the project's root can be specified."""
        cli.main(['uninstall', '--root', 'mock/path/to/root'])
        mock_uninstall.assert_called_once_with(root='mock/path/to/root',
                                               force=False)

    @patch('gdm.commands.delete')
    def test_uninstall_force(self, mock_uninstall):
        """Verify the 'uninstall' command can be forced."""
        cli.main(['uninstall', '--force'])
        mock_uninstall.assert_called_once_with(root=None, force=True)


class TestList:

    """Unit tests for the `list` command."""

    @patch('gdm.commands.display')
    def test_list(self, mock_display):
        """Verify the 'list' command can be run."""
        cli.main(['list'])
        mock_display.assert_called_once_with(root=None, allow_dirty=True)

    @patch('gdm.commands.display')
    def test_list_root(self, mock_display):
        """Verify the project's root can be specified."""
        cli.main(['list', '--root', 'mock/path/to/root'])
        mock_display.assert_called_once_with(root='mock/path/to/root',
                                             allow_dirty=True)

    @patch('gdm.commands.display')
    def test_list_no_dirty(self, mock_display):
        """Verify the 'list' command can be set to fail when dirty."""
        cli.main(['list', '--no-dirty'])
        mock_display.assert_called_once_with(root=None, allow_dirty=False)


class TestLogging:

    """Unit tests for logging."""

    arg_verbosity = [
        ('', 0),
        ('-v', 1),
        ('-vv', 2),
        ('-vvv', 3),
        ('-vvvv', 4),
        ('-vvvvv', 4),
        ('-q', -1),
    ]

    @staticmethod
    def mock_function(*args, **kwargs):
        """Placeholder logic for logging tests."""
        logging.debug(args)
        logging.debug(kwargs)
        logging.warning("warning")
        logging.error("error")
        return True

    @pytest.mark.parametrize("arg,verbosity", arg_verbosity)
    def test_level(self, arg, verbosity):
        """Verify verbose level can be set."""
        cli.main([arg] if arg else [], self.mock_function)
        assert verbosity == common.verbosity
