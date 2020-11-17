# pylint: disable=no-self-use,redefined-outer-name,misplaced-comparison-constant

from copy import copy
from unittest.mock import Mock, patch

import pytest

from gitman.models import Source


@pytest.fixture
def source():
    return Source(type='git', repo='repo', name='name', rev='rev', link='link')


class TestSource:
    def test_init_defaults(self):
        """Verify a source has a default revision."""
        source = Source(type='git', repo='http://example.com/foo/bar.git', name=None)

        assert 'http://example.com/foo/bar.git' == source.repo
        assert 'bar' == source.name
        assert 'master' == source.rev
        assert None is source.link

    def test_init_rev(self):
        """Verify the revision can be customized."""
        source = Source(
            type='git', repo='http://mock.git', name='mock_name', rev='v1.0'
        )

        assert 'v1.0' == source.rev

    def test_init_link(self):
        """Verify the link can be set."""
        source = Source(
            type='git', repo='http://mock.git', name='mock_name', link='mock/link'
        )

        assert 'mock/link' == source.link

    def test_repr(self, source):
        """Verify sources can be represented."""
        assert "<source ['git'] 'repo' @ 'rev' in 'name' <- 'link'>" == repr(source)

    def test_repr_no_link(self, source):
        """Verify sources can be represented."""
        source.link = None

        assert "<source ['git'] 'repo' @ 'rev' in 'name'>" == repr(source)

    def test_eq(self, source):
        source2 = copy(source)
        assert source == source2

        source2.name = "dir2"
        assert source != source2

    def test_lt(self):
        sources = [
            Source(type='git', repo='http://github.com/owner/123.git', name=None),
            Source(type='git', repo='bbb', name='456'),
            Source(type='git', repo='ccc', name='456'),
            Source(type='git', repo='BBB', name='AAA'),
            Source(type='git', repo='AAA', name='AAA'),
        ]

        assert sources == sorted(sources)

    @patch('os.path.exists', Mock(return_value=False))
    @patch('gitman.shell.cd', Mock(return_value=True))
    @patch('gitman.git.valid', Mock(return_value=True))
    @patch('gitman.git.changes', Mock(return_value=False))
    @patch('gitman.git.update')
    @patch('gitman.git.fetch')
    @patch('gitman.git.is_fetch_required')
    @patch('gitman.git.clone')
    def test_update_files(
        self, mock_clone, mock_is_fetch_required, mock_fetch, mock_update
    ):
        """Verify update_files when path does not exist"""
        source = Source(type='git', repo='repo', name='name', rev='rev', link='link')
        source.update_files()

        mock_clone.assert_called_once_with(
            'git', 'repo', 'name', rev='rev', sparse_paths=[]
        )
        mock_is_fetch_required.assert_called_once_with('git', 'rev')
        mock_fetch.assert_called_once_with('git', 'repo', 'name', rev='rev')
        mock_update.assert_called_once_with(
            'git', 'repo', 'name', clean=True, fetch=False, rev='rev'
        )

    @patch('os.path.isdir', Mock(return_value=True))
    @patch('os.listdir', Mock(return_value=['test_file']))
    @patch('gitman.shell.cd', Mock(return_value=True))
    @patch('gitman.git.valid', Mock(return_value=False))
    @patch('gitman.git.changes', Mock(return_value=False))
    @patch('gitman.git.update')
    @patch('gitman.git.fetch')
    @patch('gitman.git.is_fetch_required')
    @patch('gitman.git.clone')
    def test_update_files_invalid_repo(
        self, mock_clone, mock_is_fetch_required, mock_fetch, mock_update
    ):
        """Verify update_files throws exception on invalid repo when not forced"""
        source = Source(type='git', repo='repo', name='name', rev='rev', link='link')

        with pytest.raises(Exception):
            source.update_files()

        mock_clone.assert_not_called()
        mock_is_fetch_required.assert_not_called()
        mock_fetch.assert_not_called()
        mock_update.assert_not_called()

    @patch('os.path.isdir', Mock(return_value=True))
    @patch('os.listdir', Mock(return_value=['test_file']))
    @patch('gitman.shell.cd', Mock(return_value=True))
    @patch('gitman.git.valid', Mock(return_value=False))
    @patch('gitman.git.changes', Mock(return_value=False))
    @patch('gitman.git.update')
    @patch('gitman.git.fetch')
    @patch('gitman.git.is_fetch_required')
    @patch('gitman.git.rebuild')
    @patch('gitman.git.clone')
    def test_update_files_rebuild_git(
        self, mock_clone, mock_rebuild, mock_is_fetch_required, mock_fetch, mock_update
    ):
        """Verify update_files rebuilds when invalid repo and force is passed"""
        source = Source(type='git', repo='repo', name='name', rev='rev', link='link')
        source.update_files(force=True)

        mock_clone.assert_not_called()
        mock_rebuild.assert_called_once_with('git', 'repo')
        mock_is_fetch_required.assert_not_called()
        mock_fetch.assert_called_once_with('git', 'repo', 'name', rev='rev')
        mock_update.assert_called_once_with(
            'git', 'repo', 'name', clean=True, fetch=True, rev='rev'
        )

    def test_identify_missing(self, source, tmpdir):
        """Verify a missing source identifies as unknown."""
        tmpdir.chdir()
        with patch('os.path.isdir', Mock(return_value=False)):
            assert (str(tmpdir), '<missing>', '<unknown>') == source.identify()

    def test_lock_uses_the_identity_rev(self, source):
        source.identify = Mock(return_value=('path2', 'dir2', 'abc123'))

        source2 = source.lock()

        assert 'abc123' == source2.rev
        assert 'name' == source2.name
