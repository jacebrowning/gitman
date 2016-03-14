"""Shared exepections."""


class InvalidConfig(ValueError):
    """Raised when the configuration file is invalid."""


class ShellError(Exception):
    """Raised when a shell call has a non-zero return code."""


class InvalidRepository(RuntimeError):
    """Raised when there is a problem with the checked out directory."""


class UncommittedChanges(RuntimeError):
    """Raised when uncommitted changes are not expected."""
