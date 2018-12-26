# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-variable,expression-not-assigned

from unittest.mock import Mock, call

from expecter import expect

from gitman import common
from gitman.common import _Config


class TestShowConsole:
    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = 0
        self.file = Mock()

    def test_show(self):
        common.show("Hello, world!", file=self.file, color=None)

        assert [call.write("Hello, world!"), call.write("\n")] == self.file.mock_calls

    def test_show_after_indent(self):
        common.indent()
        common.show("|\n", file=self.file, color=None)

        assert [call.write("  |\n"), call.write("\n")] == self.file.mock_calls

    def test_show_after_1_indent_2_dedent(self):
        common.indent()
        common.dedent()
        common.dedent()
        common.show("|\n", file=self.file, color=None)

        assert [call.write("|\n"), call.write("\n")] == self.file.mock_calls


class TestShowLog:
    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = 1
        self.log = Mock()

    def test_show(self):
        common.show("Hello, world!", log=self.log, color=None)

        assert [call.info("Hello, world!")] == self.log.mock_calls

    def test_show_errors(self):
        common.show("Oops", color='error', log=self.log)

        expect(self.log.mock_calls) == [call.error("Oops")]

    def test_show_after_indent(self):
        common.indent()
        common.show("|\n", log=self.log, color=None)

        assert [call.info("|")] == self.log.mock_calls

    def test_show_after_1_indent_2_dedent(self):
        common.indent()
        common.dedent()
        common.dedent()
        common.show("|\n", log=self.log, color=None)

        assert [call.info("|")] == self.log.mock_calls


class TestShowQuiet:
    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = -1
        self.file = Mock()
        self.log = Mock()

    def test_show(self):
        common.show("Hello, world!", file=self.file, log=self.log, color=None)

        assert [] == self.file.mock_calls
        assert [] == self.log.mock_calls


def describe_show():
    def it_requries_color_with_messages():
        with expect.raises(AssertionError):
            common.show("Hello, world!", 'foobar')


def describe_style():
    def when_no_color_support():
        msg = common.style("_foo_")

        expect(msg) == "_foo_"

    def when_no_message():
        msg = common.style("", _color_support=True)

        expect(msg) == ""

    def when_shell():
        msg = common.style("$ _foo_", 'shell', _color_support=True)

        expect(msg) == "\x1b[1m\x1b[32m$ \x1b[0m_foo_"

    def when_color():
        msg = common.style("_foo_", 'message', _color_support=True)

        expect(msg) == "\x1b[1m\x1b[37m_foo_\x1b[0m"

    def when_unknown_color():
        with expect.raises(AssertionError):
            common.style("_foo_", 'bar', _color_support=True)
