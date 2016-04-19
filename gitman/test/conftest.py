"""Unit test configuration."""

import os
import logging

import pytest
import yorm


ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, 'files')


def pytest_configure(config):
    """Conigure logging and silence verbose test runner output."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-8s] (%(name)s @%(lineno)4d) %(message)s",
    )
    logging.getLogger('yorm').setLevel(logging.WARNING)

    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


def pytest_runtest_setup(item):
    """Disable YORM file storage during unit tests."""
    if 'integration' in item.keywords:
        if not os.getenv(ENV):
            pytest.skip(REASON)
        else:
            yorm.settings.fake = False
    else:
        yorm.settings.fake = True
