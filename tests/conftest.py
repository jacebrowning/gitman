"""pytest configuration."""

import os

import yorm

from gdm.test.conftest import pytest_configure  # pylint:disable=unused-import


ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, 'files')


def pytest_runtest_setup(item):
    """pytest setup."""
    if 'integration' in item.keywords:
        yorm.settings.fake = False
    else:
        yorm.settings.fake = True
