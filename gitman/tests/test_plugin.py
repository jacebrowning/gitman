# pylint: disable=no-self-use

from unittest.mock import call, patch

from gitman import plugin


class TestMain:

    """Unit tests for the top-level arguments."""

    @patch('gitman.cli.commands')
    def test_install(self, mock_commands):
        """Verify 'install' is the default command."""
        mock_commands.install.__name__ = 'mock'

        plugin.main([])

        assert [
            call.install(
                root=None,
                depth=None,
                clean=False,
                fetch=True,
                force=False,
                force_interactive=False,
                skip_changes=False,
            ),
            call.install().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_update(self, mock_commands):
        """Verify 'update' can be called with cleaning."""
        mock_commands.update.__name__ = 'mock'

        plugin.main(['--update', '--clean'])

        assert [
            call.update(
                root=None,
                depth=None,
                clean=True,
                force=False,
                force_interactive=False,
                recurse=False,
                lock=True,
                skip_changes=False,
            ),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_update_recursive(self, mock_commands):
        """Verify 'update' can be called recursively."""
        mock_commands.update.__name__ = 'mock'

        plugin.main(['--update', '--all'])

        assert [
            call.update(
                root=None,
                depth=None,
                clean=False,
                force=False,
                force_interactive=False,
                recurse=True,
                lock=True,
                skip_changes=False,
            ),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_update_no_lock(self, mock_commands):
        """Verify 'update' can be called without locking."""
        mock_commands.update.__name__ = 'mock'

        plugin.main(['--update', '--skip-lock'])

        assert [
            call.update(
                root=None,
                depth=None,
                clean=False,
                force=False,
                force_interactive=False,
                recurse=False,
                lock=False,
                skip_changes=False,
            ),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_update_skip_changes(self, mock_commands):
        """Verify the 'update' command with skip changes option."""
        mock_commands.update.__name__ = 'mock'

        plugin.main(['--update', '--skip-changes'])

        assert [
            call.update(
                root=None,
                depth=None,
                clean=False,
                force=False,
                force_interactive=False,
                recurse=False,
                lock=True,
                skip_changes=True,
            ),
            call.update().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_list(self, mock_commands):
        """Verify 'list' can be called."""
        mock_commands.display.__name__ = 'mock'

        plugin.main(['--list'])

        assert [
            call.display(root=None, depth=None, allow_dirty=True),
            call.display().__bool__(),  # command status check
        ] == mock_commands.mock_calls

    @patch('gitman.cli.commands')
    def test_uninstall(self, mock_commands):
        """Verify 'clean' can be called with force."""
        mock_commands.delete.__name__ = 'mock'

        plugin.main(['--uninstall', '--force'])

        assert [
            call.delete(root=None, force=True, keep_location=False),
            call.delete().__bool__(),  # command status check
        ] == mock_commands.mock_calls
