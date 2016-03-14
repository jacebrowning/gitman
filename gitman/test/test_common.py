# pylint: disable=attribute-defined-outside-init

from unittest.mock import Mock, call

from gitman import common
from gitman.common import _Config


class TestShowConsole:

    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = 0
        self.file = Mock()

    def test_show(self):
        common.show("Hello, world!", file=self.file)

        assert [
            call.write("Hello, world!"),
            call.write("\n"),
        ] == self.file.mock_calls

    def test_show_after_indent(self):
        common.indent()
        common.show("|\n", file=self.file)

        assert [
            call.write("  |\n"),
            call.write("\n"),
        ] == self.file.mock_calls

    def test_show_after_1_indent_2_dedent(self):
        common.indent()
        common.dedent()
        common.dedent()
        common.show("|\n", file=self.file)

        assert [
            call.write("|\n"),
            call.write("\n"),
        ] == self.file.mock_calls


class TestShowLog:

    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = 1
        self.log = Mock()

    def test_show(self):
        common.show("Hello, world!", log=self.log)

        assert [
            call.info("Hello, world!"),
        ] == self.log.mock_calls

    def test_show_after_indent(self):
        common.indent()
        common.show("|\n", log=self.log)

        assert [
            call.info("|"),
        ] == self.log.mock_calls

    def test_show_after_1_indent_2_dedent(self):
        common.indent()
        common.dedent()
        common.dedent()
        common.show("|\n", log=self.log)

        assert [
            call.info("|"),
        ] == self.log.mock_calls


class TestShowQuiet:

    def setup_method(self, _):
        _Config.indent_level = 0
        _Config.verbosity = -1
        self.file = Mock()
        self.log = Mock()

    def test_show(self):
        common.show("Hello, world!", file=self.file, log=self.log)

        assert [] == self.file.mock_calls
        assert [] == self.log.mock_calls
