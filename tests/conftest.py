"""pytest configuration."""
# pylint:disable=E1101

import os

import pytest
import yorm


ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, 'files')


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


def pytest_runtest_setup(item):
    """pytest setup."""
    if 'integration' in item.keywords:
        yorm.settings.fake = False
    else:
        yorm.settings.fake = True
