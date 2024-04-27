# pylint: disable=expression-not-assigned

import os
from unittest.mock import Mock, patch

import pytest
from expecter import expect

from gitman import shell
from gitman.exceptions import ShellError

from .utils import check_calls


class TestCall:
    """Tests for interacting with the shell."""

    def test_other_error_uncaught(self):
        """Verify program errors raise exceptions."""
        with pytest.raises(ShellError):
            shell.call("git", "--invalid-git-argument")

    def test_other_error_ignored(self):
        """Verify program errors can be ignored."""
        shell.call("git", "--invalid-git-argument", _ignore=True)

    def test_other_capture(self):
        """Verify a program's output can be captured."""
        if os.name == "nt":
            lines = shell.call("echo Hello, world!", _shell=True)
        else:
            lines = shell.call("echo", "Hello, world!")

        expect(lines) == ["Hello, world!"]


@patch("gitman.shell.call")
class TestPrograms:
    """Tests for calls to shell programs."""

    def test_mkdir(self, mock_call):
        """Verify the commands to create directories."""
        shell.mkdir("mock/dirpath")
        if os.name == "nt":
            check_calls(mock_call, ["mkdir mock/dirpath"])
        else:
            check_calls(mock_call, ["mkdir -p mock/dirpath"])

    @patch("os.chdir")
    def test_cd(self, mock_chdir, mock_call):
        """Verify the commands to change directories."""
        shell.cd("mock/dirpath")
        mock_chdir.assert_called_once_with("mock/dirpath")
        check_calls(mock_call, [])

    @patch("os.getcwd", Mock(return_value="mock/dirpath"))
    @patch("gitman.shell.show")
    def test_pwd(self, mock_show, mock_call):
        """Verify the commands to get current working directory."""
        result = shell.pwd()
        mock_show.assert_called_once_with("cwd", "mock/dirpath", stdout=True)
        check_calls(mock_call, [])
        assert "mock/dirpath" == result

    @patch("os.path.isdir", Mock(return_value=True))
    @patch("os.symlink")
    def test_ln(self, mock_symlink, mock_call):
        """Verify the commands to create symbolic links."""
        shell.ln("mock/target", "mock/source")
        mock_symlink.assert_called_once_with("mock/target", "mock/source")
        check_calls(mock_call, [])

    @patch("os.path.isdir", Mock(return_value=False))
    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.symlink")
    def test_ln_missing_parent(self, mock_symlink, mock_call):
        """Verify the commands to create symbolic links (missing parent)."""
        shell.ln("mock/target", "mock/source")
        mock_symlink.assert_called_once_with("mock/target", "mock/source")
        if os.name == "nt":
            check_calls(mock_call, ["mkdir mock"])
        else:
            check_calls(mock_call, ["mkdir -p mock"])

    @patch("os.path.isfile", Mock(return_value=True))
    def test_rm_file(self, mock_call):
        """Verify the commands to delete files."""
        shell.rm("mock/path")
        if os.name == "nt":
            check_calls(mock_call, ["del /Q /F mock/path"])
        else:
            check_calls(mock_call, ["rm -rf mock/path"])

    @patch("os.path.isdir", Mock(return_value=True))
    def test_rm_directory(self, mock_call):
        """Verify the commands to delete directories."""
        shell.rm("mock/dirpath")
        if os.name == "nt":
            check_calls(mock_call, ["rmdir /Q /S mock/dirpath"])
        else:
            check_calls(mock_call, ["rm -rf mock/dirpath"])
