"""Integration tests for the `gdm` package."""

from .conftest import FILES
import subprocess

import pytest

import gdm
from gdm.config import Config


@pytest.mark.integration
def test_install():

    # TODO: add assertions to this test

    # clean install
    config = Config(FILES)
    subprocess.call(['rm', '-rf', config.location])
    gdm.install(FILES)

    # second install
    gdm.install(FILES)
