"""Unit tests for the `commands` module."""
# pylint: disable=R0201

import os

from .conftest import ROOT, FILES

from gdm.commands import _find_root

PROJECT_ROOT = os.path.dirname(os.path.dirname(ROOT))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)


class TestFindRoot:

    def test_specified(self):
        assert FILES == _find_root(FILES)

    def test_none(self):
        assert PROJECT_ROOT == _find_root(None, cwd=ROOT)

    def test_current(self):
        assert PROJECT_ROOT == _find_root(PROJECT_ROOT, cwd=ROOT)

    def test_missing(self):
        assert PROJECT_PARENT == _find_root(None, cwd=PROJECT_PARENT)
