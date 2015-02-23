"""Integration tests for the `gdm` package."""

import os
import shutil

import pytest

import gdm
from gdm.config import Config

from .conftest import FILES


@pytest.mark.integration
def test_install():
    """Verify dependencies can be installed."""
    config = Config(FILES)
    if os.path.exists(config.location):
        shutil.rmtree(config.location)
    assert not os.path.exists(config.location)

    # clean install
    assert gdm.install(FILES)
    assert os.path.isdir(config.location)
    # second install
    assert gdm.install(FILES)
    assert 'gdm_1' in os.listdir(config.location)
    assert 'gdm_2' in os.listdir(config.location)

    shutil.rmtree(os.path.join(FILES, 'src'))
