"""pytest configuration."""
# pylint:disable=E1101

import os

import pytest
import yorm

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, 'files')


def pytest_runtest_setup(item):
    """pytest setup."""
    if 'integration' in item.keywords:
        if not os.getenv(ENV):
            pytest.skip(REASON)
        else:
            yorm.settings.fake = False
    else:
        yorm.settings.fake = True
