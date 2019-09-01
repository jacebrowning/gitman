"""Program defaults."""

import os

import log


# Cache settings
CACHE = os.path.expanduser(os.getenv('GITMAN_CACHE', "~/.gitcache"))
CACHE_DISABLE = bool(os.getenv('GITMAN_CACHE_DISABLE'))

# Logging settings
DEFAULT_LOGGING_FORMAT = "%(message)s"
LEVELED_LOGGING_FORMAT = "%(levelname)s: %(message)s"
VERBOSE_LOGGING_FORMAT = "[%(levelname)-8s] %(message)s"
VERBOSE2_LOGGING_FORMAT = "[%(levelname)-8s] (%(name)s @%(lineno)4d) %(message)s"
QUIET_LOGGING_LEVEL = log.ERROR
DEFAULT_LOGGING_LEVEL = log.WARNING
VERBOSE_LOGGING_LEVEL = log.INFO
VERBOSE2_LOGGING_LEVEL = log.DEBUG
LOGGING_DATEFMT = "%Y-%m-%d %H:%M"

# 3rd party settings
YORM_LOGGING_LEVEL = log.WARNING
SH_LOGGING_LEVEL = log.WARNING
