"""Package for GDM."""

import sys

__project__ = 'GDM'
__version__ = '0.1a2'

CLI = 'gdm'
VERSION = __project__ + '-' + __version__
DESCRIPTION = "A very basic language-agnostic dependency manager using Git."

PYTHON_VERSION = 3, 3

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from .commands import install
except ImportError:  # pragma: no cover (manual test)
    pass
