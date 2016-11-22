"""Package entry point."""

# Declare itself as package if needed
if __name__ == '__main__' and __package__ is None:
    import os, sys, importlib
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(parent_dir))
    __package__ = os.path.basename(parent_dir)
    importlib.import_module(__package__)

from gitman.cli import main


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
