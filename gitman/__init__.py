"""Package for GitMan."""

from pkg_resources import get_distribution

from .commands import delete as uninstall  # pylint: disable=redefined-builtin
from .commands import display as list
from .commands import init, install, lock, update

__version__ = get_distribution("gitman").version
