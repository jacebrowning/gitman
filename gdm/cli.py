#!/usr/bin/env python

"""Command-line interface."""

import os
import sys
# import argparse

# from . import CLI, VERSION, DESCRIPTION
from . import commands


def main(args=None):
    """Process command-line arguments and run the program."""

    args = sys.argv if args is None else args

    assert len(args) == 2
    root = os.path.abspath(args[1])

    run(root)


def run(root):
    """Run the program."""

    commands.install(root)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
