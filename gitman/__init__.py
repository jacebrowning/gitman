from importlib.metadata import PackageNotFoundError, version

from .commands import delete as uninstall
from .commands import display as list
from .commands import init, install, lock, update

try:
    __version__ = version("gitman")
except PackageNotFoundError:
    __version__ = "(local)"


del PackageNotFoundError
del version
