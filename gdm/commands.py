"""Functions to manage the installation of dependencies."""

import os

from . import config


def install(root=None):
    """Install dependencies for a project."""

    if root is None:
        root = os.getcwd()

    config.install_deps(root)

    return True
