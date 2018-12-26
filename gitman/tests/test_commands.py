# pylint: disable=redefined-outer-name,unused-argument,unused-variable,singleton-comparison,expression-not-assigned

from expecter import expect

from gitman import commands


def describe_install():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.install()) == False


def describe_update():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.update()) == False


def describe_display():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.display()) == False


def describe_lock():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.lock()) == False


def describe_delete():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.delete()) == False


def describe_show():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.show()) == False


def describe_edit():
    def can_be_run_without_project(tmpdir):
        tmpdir.chdir()

        expect(commands.show()) == False
