"""Integration tests for the `gdm` package."""

import os
import shutil

import pytest

import gdm
from gdm.config import Config

from .conftest import FILES, ROOT



@pytest.mark.integration
class TestInstallAndGet:

    def teardown_method(self, _):
        os.chdir(ROOT)

    def test_install(self):
        """Verify dependencies can be installed."""
        config = Config(FILES)
        shutil.rmtree(config.location, ignore_errors=True)
        assert not os.path.exists(config.location)

        # clean install
        assert gdm.install(FILES)
        assert os.path.isdir(config.location)
        # second install
        assert gdm.install(FILES)
        assert 'gdm_1' in os.listdir(config.location)
        assert 'gdm_2' in os.listdir(config.location)

    def test_uninstall(self):
        """Verify dependencies can be uninstalled."""
        config = Config(FILES)

        assert gdm.install(FILES)
        assert os.path.isdir(config.location)

        assert gdm.uninstall(FILES)
        assert not os.path.isdir(config.location)
