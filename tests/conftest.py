"""Integration tests configuration."""
# pylint: disable=unused-argument

import yorm

from gitman.test.conftest import pytest_configure  # pylint: disable=unused-import


def pytest_runtest_setup(item):
    """Ensure files are created for integration tests."""
    yorm.settings.fake = False
