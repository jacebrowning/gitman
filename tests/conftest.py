"""Integration tests configuration file."""

import yorm

from gitman.tests.conftest import pytest_configure  # pylint: disable=unused-import


def pytest_runtest_setup(item):  # pylint: disable=unused-argument
    """Ensure files are created for integration tests."""
    yorm.settings.fake = False
