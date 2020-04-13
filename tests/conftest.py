"""Integration tests configuration file."""

# pylint: disable=unused-import

import datafiles

from gitman.tests.conftest import pytest_configure


def pytest_runtest_setup(item):  # pylint: disable=unused-argument
    """Ensure files are created for integration tests."""
    datafiles.settings.HOOKS_ENABLED = True
