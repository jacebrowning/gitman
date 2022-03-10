# pylint: disable=no-self-use,redefined-outer-name,unused-variable,expression-not-assigned,misplaced-comparison-constant,len-as-condition

import os

import pytest
from expecter import expect

from gitman.models import Config, load_config

from .conftest import FILES


class TestConfig:
    def test_init_defaults(self):
        """Verify a config has a default filename and location."""
        config = Config("mock/root")

        assert "mock/root" == config.root
        assert "gitman.yml" == config.filename
        assert "gitman_sources" == config.location
        assert [] == config.sources

    def test_init_filename(self):
        """Verify the filename can be customized."""
        config = Config("mock/root", "mock.custom")

        assert "mock.custom" == config.filename
        assert "gitman_sources" == config.location

    def test_init_location(self):
        """Verify the location can be customized."""
        config = Config("mock/root", location=".gitman")

        assert "gitman.yml" == config.filename
        assert ".gitman" == config.location

    def test_path(self):
        """Verify the path is correct."""
        config = Config("mock/root")

        assert os.path.normpath("mock/root/gitman.yml") == config.path

    @pytest.mark.integration
    def test_install_and_list(self):
        """Verify the correct dependencies are installed."""
        config = Config(FILES)

        count = config.install_dependencies()
        assert 7 == count

        items = list(config.get_dependencies(nested=False))
        assert 7 == len(items)
        assert "dfd561870c0eb6e814f8f6cd11f8f62f4ae88ea0" == items[0][2]
        assert "050290bca3f14e13fd616604202b579853e7bfb0" == items[1][2]
        assert "fb693447579235391a45ca170959b5583c5042d8" == items[2][2]
        # master branch always changes                       items[3][2]
        # master branch always changes                       items[4][2]
        assert "7bd138fe7359561a8c2ff9d195dff238794ccc04" == items[5][2]
        assert "2da24fca34af3748e3cab61db81a2ae8b35aec94" == items[6][2]

        assert 5 == len(list(config.get_dependencies(depth=2, nested=False)))

        assert 3 == len(list(config.get_dependencies(depth=1, nested=False)))

        assert 0 == len(list(config.get_dependencies(depth=0, nested=False)))

    @pytest.mark.integration
    def test_install_with_dirs(self):
        """Verify the dependency list can be filtered."""
        config = Config(FILES)

        count = config.install_dependencies("gitman_2", "gitman_3")
        assert 2 == count

    def test_install_with_dirs_unknown(self):
        """Verify zero dependencies are installed with unknown dependency."""
        config = Config(FILES)

        count = config.install_dependencies("foobar")
        assert 0 == count

    def test_install_with_depth_0(self):
        """Verify an install depth of 0 installs nothing."""
        config = Config(FILES)

        count = config.install_dependencies(depth=0)
        assert 0 == count

    @pytest.mark.integration
    def test_install_with_depth_1(self):
        """Verify an install depth of 1 installs the direct dependencies."""
        config = Config(FILES)

        count = config.install_dependencies(depth=1)
        assert 3 == count

    @pytest.mark.integration
    def test_install_with_depth_2(self):
        """Verify an install depth of 2 installs 1 level of nesting."""
        config = Config(FILES)

        count = config.install_dependencies(depth=2)
        assert 5 == count


def describe_config():
    @pytest.fixture
    def config():
        return Config("m/root", "m.ext", "m/location")

    def describe_get_path():
        def it_defaults_to_sources_location(config):
            expect(config.get_path()) == os.path.normpath("m/root/m/location")

        def it_can_get_the_config_path(config):
            expect(config.get_path("__config__")) == os.path.normpath("m/root/m.ext")

        def it_can_get_log_path(config):
            expect(config.get_path("__log__")) == os.path.normpath(
                "m/root/m/location/gitman.log"
            )

        def it_can_get_dependency_path(config):
            expect(config.get_path("foobar")) == os.path.normpath(
                "m/root/m/location/foobar"
            )


class TestLoad:
    def test_load_from_directory_with_config_file(self):
        config = load_config(FILES)

        assert None is not config

    def test_load_from_directory_without_config_file(self, tmpdir):
        tmpdir.chdir()

        config = load_config()

        assert None is config
