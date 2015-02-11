"""Integration tests for the `gdm` package."""

from . import FILES


import gdm


def test_install():
    gdm.install(FILES)
