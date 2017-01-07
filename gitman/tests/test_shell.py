# pylint: disable=no-self-use,misplaced-comparison-constant

import os

from unittest.mock import patch, Mock

import pytest
from gitman import shell
from gitman.exceptions import ShellError

from . import assert_calls


class TestCall:
    """Tests for interacting with the shell."""

    def test_other_error_uncaught(self):
        """Verify program errors raise exceptions."""
        with pytest.raises(ShellError):
            shell.call('git', '--invalid-git-argument')

    def test_other_error_ignored(self):
        """Verify program errors can be ignored."""
        shell.call('git', '--invalid-git-argument', _ignore=True)

    def test_other_capture(self):
        """Verify a program's output can be captured."""
        if os.name == 'nt':
            stdout = shell.call('echo', 'Hello, world!', _shell=True)
            assert '"Hello, world!"' == stdout
        else:
            stdout = shell.call('echo', 'Hello, world!\n')
            assert "Hello, world!" == stdout


@patch('gitman.shell.call')
class TestPrograms:
    """Tests for calls to shell programs."""

    def test_mkdir(self, mock_makedirs, mock_call):
        """Verify the commands to create directories."""
        shell.mkdir('mock/dirpath')
        if os.name == 'nt':
            assert_calls(mock_call, ["mkdir mock/name/path"])
        else:
            assert_calls(mock_call, ["mkdir -p mock/name/path"])
        

    @patch('os.chdir')
    def test_cd(self, mock_chdir, mock_call):
        """Verify the commands to change directories."""
        shell.cd('mock/dirpath')
        mock_chdir.assert_called_once_with('mock/dirpath')
        assert_calls(mock_call, [])

    @patch('os.path.isdir', Mock(return_value=True))
    @pytest.mark.skipif(os.name == 'nt', reason="no symlink on Windows")
    def test_ln(self, mock_call):
        """Verify the commands to create symbolic links."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["ln -s mock/target mock/source"])

    @patch('os.path.isdir', Mock(return_value=False))
    @pytest.mark.skipif(os.name == 'nt', reason="no symlink on Windows")
    def test_ln_missing_parent(self, mock_call):
        """Verify the commands to create symbolic links (missing parent)."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["mkdir -p mock",
                                 "ln -s mock/target mock/source"])

    @patch('os.path.exists', Mock(return_value=True))
    def test_rm_file(self, mock_remove, mock_call):
        """Verify the commands to delete files."""
        shell.rm('mock/path')
        if os.name == 'nt':
            assert_calls(mock_call, ["del /Q /F mock/path"])
        else:
            assert_calls(mock_call, ["rm -rf mock/path"])

    @patch('os.path.exists', Mock(return_value=True))
    @patch('os.path.isdir', Mock(return_value=True))
    def test_rm_directory(self, mock_rmtree, mock_call):
        """Verify the commands to delete directories."""
        shell.rm('mock/dirpath')
        if os.name == 'nt':
            assert_calls(mock_call, ["rmdir /Q /S mock/dirpath"])
        else:
            assert_calls(mock_call, ["rm -rf mock/dirpath"])

