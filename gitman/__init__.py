"""Package for GitMan."""

from pkg_resources import get_distribution

from .commands import (  # pylint: disable=redefined-builtin
    delete as uninstall,
    display as list,
    init,
    install,
    lock,
    update,
)


__version__ = get_distribution('gitman').version
