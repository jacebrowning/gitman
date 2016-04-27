# pylint: disable=no-self-use,expression-not-assigned,singleton-comparison

import os

from expecter import expect

from .conftest import ROOT, FILES

from gitman.commands import _find_root, install, update, display, delete

PROJECT_ROOT = ROOT.parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent


class TestCommands:

    def test_commands_can_be_run_without_project(self, tmpdir):
        tmpdir.chdir()
        expect(install()) == False
        expect(update()) == False
        expect(display()) == False
        expect(delete()) == False


class TestFindRoot:

    def test_specified(self):
        os.chdir(str(PROJECT_PARENT))
        expect(_find_root(FILES)) == FILES

    def test_none(self):
        expect(_find_root(None, cwd=ROOT)) == PROJECT_ROOT

    def test_current(self):
        expect(_find_root(PROJECT_ROOT, cwd=ROOT)) == PROJECT_ROOT

    def test_missing(self):
        expect(_find_root(None, cwd=PROJECT_PARENT)) == PROJECT_PARENT
