# pylint: disable=no-self-use

from unittest.mock import patch, Mock

import pytest

from gitman import shell
from gitman.exceptions import ShellError

from . import assert_calls


class TestCall:

    """Tests for interacting with the shell."""

    @patch('os.chdir')
    def test_cd(self, mock_chdir):
        """Verify directories are changed correctly."""
        shell.call('cd', 'mock/dir')
        mock_chdir.assert_called_once_with('mock/dir')

    @patch('gitman.shell.Command')
    def test_other(self, mock_command):
        """Verify directories are changed correctly."""
        shell.call('mock_program')
        mock_command.assert_called_once_with('mock_program')

    def test_other_error_uncaught(self):
        """Verify program errors raise exceptions."""
        with pytest.raises(ShellError):
            shell.call('git', '--invalid-git-argument')

    def test_other_error_ignored(self):
        """Verify program errors can be ignored."""
        shell.call('git', '--invalid-git-argument', _ignore=True)

    def test_other_capture(self):
        """Verify a program's output can be captured."""
        stdout = shell.call('echo', 'Hello, world!\n', _capture=True)
        assert "Hello, world!" == stdout


@patch('gitman.shell.call')
class TestPrograms:

    """Tests for calls to shell programs."""

    def test_mkdir(self, mock_call):
        """Verify the commands to create directories."""
        shell.mkdir('mock/dir/path')
        assert_calls(mock_call, ["mkdir -p mock/dir/path"])

    def test_cd(self, mock_call):
        """Verify the commands to change directories."""
        shell.cd('mock/dir/path')
        assert_calls(mock_call, ["cd mock/dir/path"])

    @patch('os.path.isdir', Mock(return_value=True))
    def test_ln(self, mock_call):
        """Verify the commands to create symbolic links."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["ln -s mock/target mock/source"])

    @patch('os.path.isdir', Mock(return_value=False))
    def test_ln_missing_parent(self, mock_call):
        """Verify the commands to create symbolic links (missing parent)."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["mkdir -p mock",
                                 "ln -s mock/target mock/source"])

    def test_rm(self, mock_call):
        """Verify the commands to delete files/folders."""
        shell.rm('mock/dir/path')
        assert_calls(mock_call, ["rm -rf mock/dir/path"])
