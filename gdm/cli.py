#!/usr/bin/env python

"""Command-line interface."""

import sys
import argparse

from . import CLI, VERSION, DESCRIPTION
from .types import Configuration

import yorm


log = common.logger(__name__)


def main(args=None):
    """Process command-line arguments and run the program."""




def run(path):
    """Run the program."""

    configuration = Configuration()
    # TODO: convert to `yorm.load()` when available
    yorm.store(configuration, path)

    for dependency in dependencies:
        dependency.update()




    return True





if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
