# pylint: disable=no-self-use,misplaced-comparison-constant

from unittest.mock import patch, Mock

import pytest
import os
from gitman import shell
from gitman.exceptions import ShellError

from . import assert_calls


class TestCall:

    """Tests for interacting with the shell."""

    @patch('os.chdir')
    def test_cd(self, mock_chdir):
        """Verify directories are changed correctly."""
        shell.call('cd', 'mock/name')
        mock_chdir.assert_called_once_with('mock/name')

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

    @pytest.mark.skip(reason="gitman.shell.mkdir do not use call function for now")
    def test_mkdir(self, mock_call):
        """Verify the commands to create directories."""
        shell.mkdir('mock/name/path')
        assert_calls(mock_call, ["mkdir -p mock/name/path"])

    def test_cd(self, mock_call):
        """Verify the commands to change directories."""
        shell.cd('mock/name/path')
        assert_calls(mock_call, ["cd mock/name/path"])

    @patch('os.path.isdir', Mock(return_value=True))
    @pytest.mark.skipif(os.name == 'nt', reason="symlink not supported on windows")
    def test_ln(self, mock_call):
        """Verify the commands to create symbolic links."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["ln -s mock/target mock/source"])

    @patch('os.path.isdir', Mock(return_value=False))
    @pytest.mark.skipif(os.name == 'nt', reason="symlink not supported on windows")
    def test_ln_missing_parent(self, mock_call):
        """Verify the commands to create symbolic links (missing parent)."""
        shell.ln('mock/target', 'mock/source')
        assert_calls(mock_call, ["ln -s mock/target mock/source"])

    @pytest.mark.skip(reason="gitman.shell.rm do not use call function for now")
    def test_rm(self, mock_call):
        """Verify the commands to delete files/folders."""
        shell.rm('mock/name/path')
        assert_calls(mock_call, ["rm -rf mock/name/path"])
