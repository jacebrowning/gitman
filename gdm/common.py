"""Common exceptions, classes, and functions."""

import sys
import argparse
import logging

from . import settings


MAX_VERBOSITY = 4

logger = logging.getLogger
verbosity = 0


class CallException(Exception):

    """Exception raised when a program call has a non-zero return code."""


class WideHelpFormatter(argparse.HelpFormatter):

    """Command-line help text formatter with wider help text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_help_position=40, **kwargs)


class WarningFormatter(logging.Formatter):

    """Logging formatter that displays verbose formatting for WARNING+."""

    def __init__(self, default_format, verbose_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_format = default_format
        self.verbose_format = verbose_format

    def format(self, record):
        """A hack to change the formatting style dynamically."""
        # pylint: disable=W0212
        if record.levelno > logging.INFO:
            self._style._fmt = self.verbose_format
        else:
            self._style._fmt = self.default_format
        return super().format(record)


def configure_logging(count=0):
    """Configure logging using the provided verbosity count."""
    assert MAX_VERBOSITY == 4

    if count == -1:
        level = settings.QUIET_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif count == 0:
        level = settings.DEFAULT_LOGGING_LEVEL
        default_format = settings.DEFAULT_LOGGING_FORMAT
        verbose_format = settings.LEVELED_LOGGING_FORMAT
    elif count == 1:
        level = settings.VERBOSE_LOGGING_LEVEL
        default_format = settings.VERBOSE_LOGGING_FORMAT
        verbose_format = settings.VERBOSE_LOGGING_FORMAT
    elif count == 2:
        level = settings.VERBOSE2_LOGGING_LEVEL
        default_format = settings.VERBOSE_LOGGING_FORMAT
        verbose_format = settings.VERBOSE_LOGGING_FORMAT
    elif count == 3:
        level = settings.VERBOSE2_LOGGING_LEVEL
        default_format = settings.VERBOSE2_LOGGING_FORMAT
        verbose_format = settings.VERBOSE2_LOGGING_FORMAT
    else:
        level = settings.VERBOSE2_LOGGING_LEVEL - 1
        default_format = settings.VERBOSE2_LOGGING_FORMAT
        verbose_format = settings.VERBOSE2_LOGGING_FORMAT

    # Set a custom formatter
    logging.basicConfig(level=level)
    logging.captureWarnings(True)
    formatter = WarningFormatter(default_format, verbose_format,
                                 datefmt=settings.LOGGING_DATEFMT)
    logging.root.handlers[0].setFormatter(formatter)
    logging.getLogger('yorm').setLevel(max(level, settings.YORM_LOGGING_LEVEL))

    # Warn about excessive verbosity
    global verbosity  # pylint: disable=W0603
    if count > MAX_VERBOSITY:
        msg = "maximum verbosity level is {}".format(MAX_VERBOSITY)
        logging.warn(msg)
        verbosity = MAX_VERBOSITY
    else:
        verbosity = count


_indent_level = 0


def indent():
    global _indent_level
    _indent_level += 1


def dedent(level=None):
    global _indent_level
    _indent_level = max(0, _indent_level - 1) if level is None else level


def show(message="", file=sys.stdout, log=logger(__name__)):
    """Write to standard output or error if enabled."""
    if verbosity == 0:
        print("  " * _indent_level + message, file=file)
    elif verbosity >= 1:
        message = message.strip()
        if message and log:
            log.info(message)
