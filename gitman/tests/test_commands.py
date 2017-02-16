# pylint: disable=redefined-outer-name,unused-argument,unused-variable,singleton-comparison,expression-not-assigned

import os

from expecter import expect

from gitman.commands import install, update, display, delete
from gitman.commands import _find_root, _find_config

from .conftest import ROOT, FILES

PROJECT_ROOT = os.path.dirname(os.path.dirname(ROOT))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)


def describe_commands():

    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        assert not install()
        assert not update()
        assert not display()
        assert not delete()


def describe_find_config():

    def when_found_in_root():
        expect(_find_config(cwd=ROOT)) != None

    def when_found_in_current_directory():
        expect(_find_config(root=ROOT, cwd=FILES)) != None

    def when_not_found():
        expect(_find_config(root=PROJECT_PARENT, cwd=PROJECT_PARENT)) == None

    def when_not_found_outside_root():
        expect(_find_config(root=PROJECT_ROOT, cwd=PROJECT_PARENT)) == None


def describe_find_root():

    def when_specified():
        os.chdir(PROJECT_PARENT)

        expect(_find_root(FILES)) == FILES

    def when_not_specified():
        expect(_find_root(None, cwd=ROOT)) == PROJECT_ROOT

    def when_matching_current_directory():
        expect(_find_root(PROJECT_ROOT, cwd=ROOT)) == PROJECT_ROOT

    def when_not_found():
        expect(_find_root(None, cwd=PROJECT_PARENT)) == PROJECT_PARENT
