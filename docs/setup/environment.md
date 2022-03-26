# Environment Setup

The following environment variables can be used to change the default behavior of GitMan.

## `GITMAN_CACHE`

GitMan utilizes local repository mirrors to cache dependencies and speed up cloning.
This variable specifies the path of a directory to store these repository references.
The default value should be overridden if `$HOME` is not set on your target system.

**Default**: `~/.gitcache`

## `GITMAN_CACHE_DISABLE`

This flag variable can be used to disable GitMan's local repository cache.
If set, a full clone will be performed for each repository.
 
**Default**: _(none)_
