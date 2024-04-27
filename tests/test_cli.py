# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

import os
from unittest.mock import call, patch

import pytest
from expecter import expect

from gitman import cli


@pytest.fixture
def config(tmpdir):
    tmpdir.chdir()
    path = str(tmpdir.join("gdm.yml"))
    with open(path, "w", encoding="utf-8"):
        pass
    return path


@pytest.fixture
def location(tmpdir):
    tmpdir.chdir()
    path = str(tmpdir.join("gdm.yml"))
    with open(path, "w", encoding="utf-8") as outfile:
        outfile.write("location: foo")
    return str(tmpdir.join("foo"))


def describe_show():
    @patch("gitman.common.show")
    def it_prints_location_by_default(show, location):
        cli.main(["show"])

        expect(show.mock_calls) == [call(location, color="path")]

    @patch("gitman.common.show")
    def it_can_print_a_dependency_path(show, location):
        cli.main(["show", "bar"])

        expect(show.mock_calls) == [call(os.path.join(location, "bar"), color="path")]

    def it_exits_when_no_config_found(tmpdir):
        tmpdir.chdir()

        with expect.raises(SystemExit):
            cli.main(["show"])
