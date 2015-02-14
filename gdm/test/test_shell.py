"""Unit tests for the `shell` module."""
# pylint: disable=R0201

from unittest.mock import patch

import pytest

from gdm.shell import _call, ShellMixin, GitMixin


class TestCall:

    """Tests for interacting with the shell."""

    @patch('os.makedirs')
    def test_mkdir(self, mock_makedirs):
        """Verify directories are created correctly."""
        _call('mkdir', '-p', 'mock/dir')
        mock_makedirs.assert_called_once_with('mock/dir')

    @patch('os.chdir')
    def test_cd(self, mock_chdir):
        """Verify directories are changed correctly."""
        _call('cd', 'mock/dir')
        mock_chdir.assert_called_once_with('mock/dir')

    @patch('gdm.shell.Command')
    def test_other(self, mock_command):
        """Verify directories are changed correctly."""
        _call('mock_program')
        mock_command.assert_called_once_with('mock_program')

    def test_other_error(self):
        """Verify program errors are handled."""
        with pytest.raises(SystemExit):
            _call('git', '--invalid-git-argument')


class _BaseTestCalls:

    """Base test class to verify shell calls are correct."""

    @staticmethod
    def assert_calls(mock_call, expected):
        """Confirm the expected list of calls matches the mock call."""
        actual = mock_call.call_args_list
        assert len(expected) == len(actual)
        for index, call in enumerate(expected):
            args = actual[index][0]
            assert call == ' ' .join(args)


@patch('gdm.shell._call')
class TestShell(_BaseTestCalls):

    """Tests for calls to shell utilities."""

    shell = ShellMixin()

    def test_mkdir(self, mock_call):
        """Verify the commands to create directories."""
        self.shell.mkdir('mock/dir/path')
        self.assert_calls(mock_call, ["mkdir -p mock/dir/path"])

    def test_cd(self, mock_call):
        """Verify the commands to change directories."""
        self.shell.cd('mock/dir/path')
        self.assert_calls(mock_call, ["cd mock/dir/path"])

    def test_ln(self, mock_call):
        """Verify the commands to create symbolic links."""
        self.shell.ln('mock/target', 'mock/source')
        self.assert_calls(mock_call, ["ln -sf mock/target mock/source"])


@patch('gdm.shell._call')
class TestGit(_BaseTestCalls):

    """Tests for calls to Git."""

    shell = GitMixin()

    def test_clone(self, mock_call):
        """Verify the commands to clone a Git repository."""
        self.shell.git_clone('mock.git', 'mock_dir')
        self.assert_calls(mock_call, [
            "git clone mock.git mock_dir",
        ])

    def test_fetch(self, mock_call):
        """Verify the commands to fetch from a Git repository."""
        self.shell.git_fetch('mock.git')
        self.assert_calls(mock_call, [
            "git remote remove origin",
            "git remote add origin mock.git",
            "git fetch --all --tags --force --prune",
        ])

    def test_revert(self, mock_call):
        """Verify the commands to revert all changes in a working tree."""
        self.shell.git_revert()
        self.assert_calls(mock_call, [
            "git clean --force -d -x",
            "git reset --hard",
        ])

    def test_update(self, mock_call):
        """Verify the commands to update a working tree to a revision."""
        self.shell.git_update('mock_rev')
        self.assert_calls(mock_call, [
            "git checkout mock_rev",
        ])
