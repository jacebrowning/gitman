"""Shared exceptions."""


class InvalidConfig(ValueError):
    """Raised when the config file is invalid."""


class ShellError(RuntimeError):
    """Raised when a shell call has a non-zero return code."""

    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop('program', None)
        self.output = kwargs.pop('output', None)
        super().__init__(*args, **kwargs)  # type: ignore


class InvalidRepository(RuntimeError):
    """Raised when there is a problem with the checked out directory."""


class UncommittedChanges(RuntimeError):
    """Raised when uncommitted changes are not expected."""


class ScriptFailure(ShellError):
    """Raised when post-install script has a non-zero exit code."""
