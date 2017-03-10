# Environment Setup

The following environment variables can be used to configure the behavior of GitMan.

## `GITMAN_CACHE`

GitMan utilizes local repository mirrors to cache dependencies and speed up cloning.
This variable specifies the path of a directory to store these repository references.
The default value should be overridden if `$HOME` is not set on your target system.

**Default**: `~/.gitcache`
