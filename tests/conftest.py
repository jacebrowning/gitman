"""Integration tests configuration."""
# pylint: disable=unused-argument

import os

import yorm

from gitman.test.conftest import pytest_configure  # pylint: disable=unused-import


# TODO: delete if unused (and files)
ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, 'files')


def pytest_runtest_setup(item):
    """Ensure files are created for integration tests."""
    yorm.settings.fake = False
