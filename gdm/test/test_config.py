"""Unit tests for the `config` module."""
# pylint: disable=R0201

import pytest

from gdm.config import Source, Config, install_deps

from .conftest import FILES


class TestSource:

    def test_init_defaults(self):
        """Verify a source has a default revision."""
        source = Source('http://mock.git', 'mock_dir')
        assert 'http://mock.git' == source.repo
        assert 'mock_dir' == source.dir
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

    def test_repr(self):
        """Verify sources can be represented."""
        source = Source(repo='repo', dir='dir', rev='rev', link='link')
        assert "<source 'repo' @ 'rev' in 'dir' <- 'link'>" == repr(source)

    def test_repr_no_link(self):
        """Verify sources can be represented."""
        source = Source(repo='repo', dir='dir', rev='rev', link=None)
        assert "<source 'repo' @ 'rev' in 'dir'>" == repr(source)


class TestConfig:

    def test_init_defaults(self):
        """Verify a configuration has a default filename and location."""
        config = Config('mock/root')
        assert 'mock/root' == config.root
        assert 'gdm.yml' == config.filename
        assert 'gdm_sources' == config.location
        assert [] == config.sources

    def test_init_filename(self):
        """Verify the filename can be customized."""
        config = Config('mock/root', 'mock.custom')
        assert 'mock.custom' == config.filename
        assert 'gdm_sources' == config.location

    def test_init_location(self):
        """Verify the location can be customized."""
        config = Config('mock/root', location='.gdm')
        assert 'gdm.yml' == config.filename
        assert '.gdm' == config.location


class TestInstall:

    @pytest.mark.integration
    def test_multiple(self):
        """Verify the correct number of dependencies is installed."""
        assert 6 == install_deps(FILES)

    @pytest.mark.integration
    def test_empty(self, tmpdir):
        """Verify zero dependencies are installed with no configuration."""
        tmpdir.chdir()
        assert 0 == install_deps(str(tmpdir))
