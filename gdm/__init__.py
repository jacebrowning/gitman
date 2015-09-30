"""Package for GDM."""

import sys

__project__ = 'GDM'
__version__ = '0.5.dev2'

CLI = 'gdm'
PLUGIN = 'deps'
VERSION = __project__ + ' v' + __version__
DESCRIPTION = "A language-agnostic \"dependency manager\" using Git."

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from .commands import install
    from .commands import update
    from .commands import display as list  # pylint: disable=redefined-builtin
    from .commands import delete as uninstall
except ImportError:  # pragma: no cover (manual test)
    pass
