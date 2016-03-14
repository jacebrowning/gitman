# pylint: disable=no-self-use

from unittest.mock import patch, Mock

from gitman import git
from gitman.exceptions import ShellError

from . import assert_calls


@patch('gitman.git.call')
class TestGit:

    """Tests for calls to Git."""

    @patch('os.path.isdir', Mock(return_value=False))
    def test_clone(self, mock_call):
        """Verify the commands to set up a new reference repository."""
        git.clone('mock.git', 'mock/path', cache='cache')
        assert_calls(mock_call, [
            "git clone --mirror mock.git cache/mock.reference",
            "git clone --reference cache/mock.reference mock.git mock/path"])

    @patch('os.path.isdir', Mock(return_value=True))
    def test_clone_from_reference(self, mock_call):
        """Verify the commands to clone a Git repository from a reference."""
        git.clone('mock.git', 'mock/path', cache='cache')
        assert_calls(mock_call, [
            "git clone --reference cache/mock.reference mock.git mock/path"])

    def test_fetch(self, mock_call):
        """Verify the commands to fetch from a Git repository."""
        git.fetch('mock.git')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_fetch_rev(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev."""
        git.fetch('mock.git', 'mock-rev')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin mock-rev",
        ])

    def test_fetch_rev_sha(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ SHA."""
        git.fetch('mock.git', 'abcdef1234' * 4)
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_fetch_rev_revparse(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev-parse."""
        git.fetch('mock.git', 'master@{2015-02-12 18:30:00}')
        assert_calls(mock_call, [
            "git remote rm origin",
            "git remote add origin mock.git",
            "git fetch --tags --force --prune origin",
        ])

    def test_changes(self, mock_call):
        """Verify the commands to check for uncommitted changes."""
        git.changes(include_untracked=True)
        assert_calls(mock_call, [
            # based on: http://stackoverflow.com/questions/3878624
            "git update-index -q --refresh",
            "git diff-index --quiet HEAD",
            "git ls-files --others --exclude-standard",
            "git status",  # used for displaying the overall status
        ])

    def test_changes_false(self, _):
        """Verify the absence of changes can be detected."""
        with patch('gitman.git.call', Mock(return_value="")):
            assert False is git.changes()

    def test_changes_false_with_untracked(self, _):
        """Verify untracked files can be detected."""
        with patch('gitman.git.call', Mock(return_value="file_1")):
            assert False is git.changes()

    def test_changes_true_when_untracked_included(self, _):
        """Verify untracked files can be detected."""
        with patch('gitman.git.call', Mock(return_value="file_1")):
            assert True is git.changes(include_untracked=True)

    def test_changes_true_when_uncommitted(self, _):
        """Verify uncommitted changes can be detected."""
        with patch('gitman.git.call', Mock(side_effect=ShellError)):
            assert True is git.changes(display_status=False)

    def test_update(self, mock_call):
        """Verify the commands to update a working tree to a revision."""
        git.update('mock_rev')
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_rev",
            "git branch --set-upstream-to origin/mock_rev",
        ])

    def test_update_branch(self, mock_call):
        """Verify the commands to update a working tree to a branch."""
        git.update('mock_branch', fetch=True)
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_branch",
            "git branch --set-upstream-to origin/mock_branch",
            "git pull --ff-only --no-rebase",
        ])

    def test_update_no_clean(self, mock_call):
        git.update('mock_rev', clean=False)
        assert_calls(mock_call, [
            "git stash",
            "git checkout --force mock_rev",
            "git branch --set-upstream-to origin/mock_rev",
        ])

    def test_update_revparse(self, mock_call):
        """Verify the commands to update a working tree to a rev-parse."""
        mock_call.return_value = "abc123"
        git.update('mock_branch@{2015-02-12 18:30:00}')
        assert_calls(mock_call, [
            "git stash",
            "git clean --force -d -x",
            "git checkout --force mock_branch",
            "git rev-list -n 1 --before='2015-02-12 18:30:00' mock_branch",
            "git checkout --force abc123",
            "git branch --set-upstream-to origin/abc123",
        ])

    def test_get_url(self, mock_call):
        """Verify the commands to get the current repository's URL."""
        git.get_url()
        assert_calls(mock_call, ["git config --get remote.origin.url"])

    def test_get_hash(self, mock_call):
        """Verify the commands to get the working tree's hash."""
        git.get_hash()
        assert_calls(mock_call, ["git rev-parse HEAD"])

    def test_get_tag(self, mock_call):
        """Verify the commands to get the working tree's tag."""
        git.get_tag()
        assert_calls(mock_call, ["git describe --tags --exact-match"])

    def test_get_branch(self, mock_call):
        """Verify the commands to get the working tree's branch."""
        git.get_branch()
        assert_calls(mock_call, ["git rev-parse --abbrev-ref HEAD"])
