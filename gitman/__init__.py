"""Package for Gitman."""

from pkg_resources import DistributionNotFound, get_distribution

from .commands import delete as uninstall
from .commands import display as list
from .commands import init, install, lock, update

try:
    __version__ = get_distribution("gitman").version
except DistributionNotFound:
    __version__ = "???"
