# pylint: disable=unused-variable,expression-not-assigned

from unittest.mock import patch, call, Mock

from expecter import expect

from gitman import system


def describe_launch():

    @patch('platform.system', Mock(return_value="Windows"))
    @patch('gitman.system._launch_windows')
    def it_opens_files(startfile):
        system.launch("fake/path")
        expect(startfile.mock_calls) == [call("fake/path")]

    @patch('platform.system', Mock(return_value="fake"))
    def it_raises_an_exception_when_platform_is_unknown():
        with expect.raises(RuntimeError):
            system.launch(None)
