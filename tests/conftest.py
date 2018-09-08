"""Integration tests configuration file."""

# pylint: disable=unused-import

import yorm

from gitman.tests.conftest import pytest_configure


def pytest_runtest_setup(item):  # pylint: disable=unused-argument
    """Ensure files are created for integration tests."""
    yorm.settings.fake = False
