"""Unit tests for the 'cli' module."""
# pylint: disable=R0201

import pytest
from unittest.mock import Mock, patch
import logging

from gdm import cli
from gdm import common


class TestMain:

    """Unit tests for the top-level arguments."""

    def test_run(self):
        """Verify the CLI can be run."""
        mock_function = Mock(return_value=True)
        cli.main([], mock_function)
        mock_function.assert_called_once_with()

    def test_run_fail(self):
        """Verify the CLI can detect errors."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(return_value=False))

    def test_help(self):
        """Verify the CLI help text can be displayed."""
        with pytest.raises(SystemExit):
            cli.main(['--help'])

    def test_interrupt(self):
        """Verify the CLI can be interrupted."""
        with pytest.raises(SystemExit):
            cli.main([], Mock(side_effect=KeyboardInterrupt))

    @patch('gdm.cli.log')
    def test_interrupt_verbose(self, mock_log):
        """Verify the CLI can be interrupted (verbose output)."""
        with pytest.raises(SystemExit):
            cli.main(['-vvvv'], Mock(side_effect=KeyboardInterrupt))
        assert mock_log.exception.call_count == 1


class TestInstall:

    """Unit tests for the `install` command."""

    @patch('gdm.commands.install')
    def test_install(self, mock_install):
        """Verify the CLI can be run."""
        cli.main(['install'])
        mock_install.assert_called_once_with(root=None)

    @patch('gdm.commands.install')
    def test_install_root(self, mock_install):
        """Verify the project's root can be specified."""
        cli.main(['install', '--root', 'mock/path/to/root'])
        mock_install.assert_called_once_with(root='mock/path/to/root')


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

    def mock_function(self, *args, **kwargs):
        """Placeholder logic for logging tests."""
        logging.debug(args)
        logging.debug(kwargs)
        logging.warning("warning")
        logging.error("error")
        return True

    @pytest.mark.parametrize("arg,verbosity", arg_verbosity)
    def test_verbose(self, arg, verbosity):
        """Verify verbose level can be set."""
        cli.main([arg] if arg else [], self.mock_function)
        assert verbosity == common.verbosity
