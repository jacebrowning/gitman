# pylint: disable=no-self-use

import os

from .conftest import ROOT, FILES

from gitman.commands import _find_root, install, update, display, delete

PROJECT_ROOT = os.path.dirname(os.path.dirname(ROOT))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)


class TestCommands:

    def test_commands_can_be_run_without_project(self, tmpdir):
        tmpdir.chdir()

        assert not install()
        assert not update()
        assert not display()
        assert not delete()


class TestFindRoot:

    def test_specified(self):
        os.chdir(PROJECT_PARENT)
        assert FILES == _find_root(FILES)

    def test_none(self):
        assert PROJECT_ROOT == _find_root(None, cwd=ROOT)

    def test_current(self):
        assert PROJECT_ROOT == _find_root(PROJECT_ROOT, cwd=ROOT)

    def test_missing(self):
        assert PROJECT_PARENT == _find_root(None, cwd=PROJECT_PARENT)
