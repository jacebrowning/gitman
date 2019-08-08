# pylint: disable=no-self-use

import os
from unittest.mock import Mock, patch

from gitman import git, settings
from gitman.exceptions import ShellError

from .utils import check_calls


@patch('gitman.git.call')
class TestGit:
    """Tests for calls to Git."""

    @patch('os.path.isdir', Mock(return_value=False))
    def test_clone(self, mock_call):
        """Verify the commands to set up a new reference repository."""
        git.clone('git', 'mock.git', 'mock/path', cache='cache')
        check_calls(
            mock_call,
            [
                "git clone --mirror mock.git "
                + os.path.normpath("cache/mock.reference"),
                "git clone --reference "
                + os.path.normpath("cache/mock.reference")
                + " mock.git "
                + os.path.normpath("mock/path"),
            ],
        )

    @patch('os.path.isdir', Mock(return_value=False))
    def test_clone_without_cache(self, mock_call):
        """Verify the commands to clone a repository."""
        settings.CACHE_DISABLE = True
        try:
            git.clone('git', 'mock.git', 'mock/path', cache='cache')
            check_calls(
                mock_call, ["git clone mock.git " + os.path.normpath("mock/path")]
            )
        finally:
            settings.CACHE_DISABLE = False

    @patch('os.path.isdir', Mock(return_value=True))
    def test_clone_from_reference(self, mock_call):
        """Verify the commands to clone a Git repository from a reference."""
        git.clone('git', 'mock.git', 'mock/path', cache='cache')
        check_calls(
            mock_call,
            [
                "git clone --reference "
                + os.path.normpath("cache/mock.reference")
                + " mock.git "
                + os.path.normpath("mock/path")
            ],
        )

    def test_fetch(self, mock_call):
        """Verify the commands to fetch from a Git repository."""
        git.fetch('git', 'mock.git', 'mock/path')
        check_calls(
            mock_call,
            [
                "git remote set-url origin mock.git",
                "git fetch --tags --force --prune origin",
            ],
        )

    def test_fetch_rev(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev."""
        git.fetch('git', 'mock.git', 'mock/path', 'mock-rev')
        check_calls(
            mock_call,
            [
                "git remote set-url origin mock.git",
                "git fetch --tags --force --prune origin mock-rev",
            ],
        )

    def test_fetch_rev_sha(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ SHA."""
        git.fetch('git', 'mock.git', 'mock/path', 'abcdef1234' * 4)
        check_calls(
            mock_call,
            [
                "git remote set-url origin mock.git",
                "git fetch --tags --force --prune origin",
            ],
        )

    def test_fetch_rev_revparse(self, mock_call):
        """Verify the commands to fetch from a Git repository w/ rev-parse."""
        git.fetch('git', 'mock.git', 'mock/path', 'master@{2015-02-12 18:30:00}')
        check_calls(
            mock_call,
            [
                "git remote set-url origin mock.git",
                "git fetch --tags --force --prune origin",
            ],
        )

    @patch('os.getcwd', Mock(return_value='mock/outside_repo/nested_repo'))
    def test_valid(self, _):
        """Verify the commands to check for a working tree and is toplevel of repo."""
        with patch(
            'gitman.git.call', Mock(return_value=['mock/outside_repo/nested_repo'])
        ):
            assert True is git.valid()

    @patch('os.getcwd', Mock(return_value='mock/outside_repo/nested_repo'))
    def test_valid_false_outside_work_tree(self, _):
        """Verify a shell error indicating it is not in a working tree returns false."""
        with patch('gitman.git.call', Mock(side_effect=ShellError)):
            assert False is git.valid()

    @patch('os.getcwd', Mock(return_value='mock/outside_repo/nested_repo'))
    def test_valid_false_current_not_toplevel(self, _):
        """Verify git toplevel matches current directory"""
        with patch('gitman.git.call', Mock(return_value=['mock/outside_repo'])):
            assert False is git.valid()

    def test_rebuild(self, mock_call):
        """Verify the commands to rebuild a Git repository"""
        git.rebuild('git', 'master@{2015-02-12 18:30:00}')
        check_calls(
            mock_call,
            ["git init", "git remote add origin master@{2015-02-12 18:30:00}"],
        )

    def test_rebuild_gitsvn(self, mock_call):
        """Verify the rebuild is ignored with git-svn type"""
        git.rebuild('git-svn', 'master@{2015-02-12 18:30:00}')
        check_calls(mock_call, [])

    def test_changes(self, mock_call):
        """Verify the commands to check for uncommitted changes."""
        git.changes('git', include_untracked=True)
        check_calls(
            mock_call,
            [
                # based on: http://stackoverflow.com/questions/3878624
                "git update-index -q --refresh",
                "git diff-index --quiet HEAD",
                "git ls-files --others --exclude-standard",
                "git status",  # used for displaying the overall status
            ],
        )

    def test_changes_false(self, _):
        """Verify the absence of changes can be detected."""
        with patch('gitman.git.call', Mock(return_value=[""])):
            assert False is git.changes('git')

    def test_changes_false_with_untracked(self, _):
        """Verify untracked files can be detected."""
        with patch('gitman.git.call', Mock(return_value=["file_1"])):
            assert False is git.changes('git')

    def test_changes_true_when_untracked_included(self, _):
        """Verify untracked files can be detected."""
        with patch('gitman.git.call', Mock(return_value=["file_1"])):
            assert True is git.changes('git', include_untracked=True)

    def test_changes_true_when_uncommitted(self, _):
        """Verify uncommitted changes can be detected."""
        with patch('gitman.git.call', Mock(side_effect=ShellError)):
            assert True is git.changes('git', display_status=False)

    def test_update(self, mock_call):
        """Verify the commands to update a working tree to a revision."""
        git.update('git', 'mock.git', 'mock/path', rev='mock_rev')
        check_calls(
            mock_call,
            [
                "git stash",
                "git clean --force -d -x",
                "git checkout --force mock_rev",
                "git branch --set-upstream-to origin/mock_rev",
            ],
        )

    def test_update_branch(self, mock_call):
        """Verify the commands to update a working tree to a branch."""
        git.update('git', 'mock.git', 'mock/path', fetch=True, rev='mock_branch')
        check_calls(
            mock_call,
            [
                "git stash",
                "git clean --force -d -x",
                "git checkout --force mock_branch",
                "git branch --set-upstream-to origin/mock_branch",
                "git pull --ff-only --no-rebase",
            ],
        )

    def test_update_no_clean(self, mock_call):
        git.update('git', 'mock.git', 'mock/path', clean=False, rev='mock_rev')
        check_calls(
            mock_call,
            [
                "git stash",
                "git checkout --force mock_rev",
                "git branch --set-upstream-to origin/mock_rev",
            ],
        )

    def test_update_revparse(self, mock_call):
        """Verify the commands to update a working tree to a rev-parse."""
        mock_call.return_value = ["abc123"]
        git.update(
            'git', 'mock.git', 'mock/path', rev='mock_branch@{2015-02-12 18:30:00}'
        )
        check_calls(
            mock_call,
            [
                "git stash",
                "git clean --force -d -x",
                "git checkout --force mock_branch",
                (
                    "git rev-list -n 1 --before='2015-02-12 18:30:00' "
                    "--first-parent mock_branch"
                ),
                "git checkout --force abc123",
                "git branch --set-upstream-to origin/abc123",
            ],
        )

    def test_get_url(self, mock_call):
        """Verify the commands to get the current repository's URL."""
        git.get_url('git')
        check_calls(mock_call, ["git config --get remote.origin.url"])

    def test_get_hash(self, mock_call):
        """Verify the commands to get the working tree's hash."""
        git.get_hash('git')
        check_calls(mock_call, ["git rev-parse HEAD"])

    def test_get_tag(self, mock_call):
        """Verify the commands to get the working tree's tag."""
        git.get_tag()
        check_calls(mock_call, ["git describe --tags --exact-match"])

    def test_get_branch(self, mock_call):
        """Verify the commands to get the working tree's branch."""
        git.get_branch()
        check_calls(mock_call, ["git rev-parse --abbrev-ref HEAD"])
