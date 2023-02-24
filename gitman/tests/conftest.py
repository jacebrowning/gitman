"""Unit test configuration file."""

import os

import datafiles
import log
import pytest

ENV = "TEST_INTEGRATION"  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)

ROOT = os.path.dirname(__file__)
FILES = os.path.join(ROOT, "files")


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False
    log.init()
    log.silence("gitman.shell", allow_info=True)
    log.silence("datafiles", allow_warning=True)


def pytest_runtest_setup(item):
    """Disable file storage during unit tests."""
    if "integration" in item.keywords:
        if not os.getenv(ENV):
            pytest.skip(REASON)
        else:
            datafiles.settings.HOOKS_ENABLED = True
    else:
        datafiles.settings.HOOKS_ENABLED = False
