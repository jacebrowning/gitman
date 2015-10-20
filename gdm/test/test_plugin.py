"""Unit tests for the 'plugin' module."""
# pylint: disable=no-self-use

from unittest.mock import patch, call

from gdm import plugin


class TestMain:

    """Unit tests for the top-level arguments."""

    @patch('gdm.cli.commands')
    def test_install(self, mock_commands):
        """Verify 'install' is the default command."""
        plugin.main([])

        assert [
            call.install(root=None, clean=False, force=False),
            call.install().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gdm.cli.commands')
    def test_update(self, mock_commands):
        """Verify 'update' can be called with cleaning."""
        plugin.main(['--update', '--clean'])

        assert [
            call.update(root=None,
                        clean=True, force=False, recurse=False, lock=True),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gdm.cli.commands')
    def test_update_recursive(self, mock_commands):
        """Verify 'update' can be called recursively."""
        plugin.main(['--update', '--all'])

        assert [
            call.update(root=None,
                        clean=False, force=False, recurse=True, lock=True),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gdm.cli.commands')
    def test_update_no_lock(self, mock_commands):
        """Verify 'update' can be called without locking."""
        plugin.main(['--update', '--no-lock'])

        assert [
            call.update(root=None,
                        clean=False, force=False, recurse=False, lock=False),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gdm.cli.commands')
    def test_list(self, mock_commands):
        """Verify 'list' can be called."""
        plugin.main(['--list'])

        assert [
            call.display(root=None, allow_dirty=True),
            call.display().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gdm.cli.commands')
    def test_uninstall(self, mock_commands):
        """Verify 'clean' can be called with force."""
        plugin.main(['--uninstall', '--force'])

        assert [
            call.delete(root=None, force=True),
            call.delete().__bool__(),  # command status check
        ] == mock_commands.mock_calls
