"""Integration tests for the `gdm` package."""
# pylint: disable=no-self-use

import os
import shutil

import pytest

import gdm
from gdm.config import Config

from .conftest import FILES, ROOT


@pytest.mark.integration
class TestCommands:

    def teardown_method(self, _):
        os.chdir(ROOT)

    def test_commands(self):
        config = Config(FILES)
        shutil.rmtree(config.location, ignore_errors=True)
        assert not os.path.exists(config.location)

        # install sources
        assert gdm.install(FILES)
        assert 'gdm_1' in os.listdir(config.location)
        assert 'gdm_2' in os.listdir(config.location)

        # list versions
        assert gdm.list(FILES)

        # update sources
        assert gdm.update(FILES)
        assert 'gdm_1' in os.listdir(config.location)
        assert 'gdm_2' in os.listdir(config.location)

        # install locked sources
        assert gdm.install(FILES)
        assert 'gdm_1' in os.listdir(config.location)
        assert 'gdm_2' in os.listdir(config.location)

        # uninstall sources
        assert gdm.uninstall(FILES)
        assert not os.path.isdir(config.location)
