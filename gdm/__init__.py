"""Package for GDM."""

import sys

__project__ = 'GDM'
__version__ = '0.0.0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 4

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))
