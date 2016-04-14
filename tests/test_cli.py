# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

import os
from unittest.mock import patch, call

import pytest
from expecter import expect

from gitman import cli


@pytest.fixture
def config(tmpdir):
    tmpdir.chdir()
    path = str(tmpdir.join("gdm.yml"))
    open(path, 'w').close()
    return path


@pytest.fixture
def location(tmpdir):
    tmpdir.chdir()
    path = str(tmpdir.join("gdm.yml"))
    with open(path, 'w') as outfile:
        outfile.write("location: foo")
    return str(tmpdir.join("foo"))


def describe_show():

    @patch('gitman.common.show')
    def it_prints_location_by_default(show, location):
        cli.main(['show'])

        expect(show.mock_calls) == [call(location)]

    @patch('gitman.common.show')
    def it_can_print_a_depenendcy_path(show, location):
        cli.main(['show', 'bar'])

        expect(show.mock_calls) == [call(os.path.join(location, "bar"))]

    def it_exits_when_no_config_found(tmpdir):
        tmpdir.chdir()

        with expect.raises(SystemExit):
            cli.main(['show'])


def describe_edit():

    @patch('gitman.system.launch')
    def it_launches_the_config(launch, config):
        cli.main(['edit'])

        expect(launch.mock_calls) == [call(config), call().__bool__()]

    def it_exits_when_no_config_found(tmpdir):
        tmpdir.chdir()

        with expect.raises(SystemExit):
            cli.main(['edit'])
