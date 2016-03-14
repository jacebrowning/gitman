# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

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


def describe_edit():

    @patch('gitman.system.launch')
    def it_launches_the_config(launch, config):
        cli.main(['edit'])

        expect(launch.mock_calls) == [call(config), call().__bool__()]

    def it_exits_when_no_config_found(tmpdir):
        tmpdir.chdir()

        with expect.raises(SystemExit):
            cli.main(['edit'])
