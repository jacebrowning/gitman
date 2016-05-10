# pylint: disable=no-self-use,redefined-outer-name

from unittest.mock import patch, Mock
from copy import copy

import pytest

from gitman.models import Source


@pytest.fixture
def source():
    return Source('repo', 'name', rev='rev', link='link')


class TestSource:

    def test_init_defaults(self):
        """Verify a source has a default revision."""
        source = Source('http://mock.git', 'mock_dir')

        assert 'http://mock.git' == source.repo
        assert 'mock_dir' == source.name
        assert 'master' == source.rev
        assert None is source.link

    def test_init_rev(self):
        """Verify the revision can be customized."""
        source = Source('http://mock.git', 'mock_dir', 'v1.0')

        assert 'v1.0' == source.rev

    def test_init_link(self):
        """Verify the link can be set."""
        source = Source('http://mock.git', 'mock_dir', link='mock/link')

        assert 'mock/link' == source.link

    def test_init_error(self):
        """Verify the repository and directory are required."""
        with pytest.raises(ValueError):
            Source('', 'mock_dir')
        with pytest.raises(ValueError):
            Source('http://mock.git', '')

    def test_repr(self, source):
        """Verify sources can be represented."""
        assert "<source 'repo' @ 'rev' in 'name' <- 'link'>" == repr(source)

    def test_repr_no_link(self, source):
        """Verify sources can be represented."""
        source.link = None

        assert "<source 'repo' @ 'rev' in 'name'>" == repr(source)

    def test_eq(self, source):
        source2 = copy(source)
        assert source == source2

        source2.name = "dir2"
        assert source != source2

    def test_lt(self):
        sources = [
            Source('zzz', '123'),
            Source('bbb', '456'),
            Source('ccc', '456'),
            Source('BBB', 'AAA'),
            Source('AAA', 'AAA'),
        ]

        assert sources == sorted(sources)

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
