# Package API

All of the [command-line interface](cli.md) functionality is available from the Python package:

```python
import gitman
```

## Init

To generate a sample config for a new project, call:

```python
gitman.init()
```

## Install

To clone/checkout the specified dependencies, call:

```python
gitman.install(*names, root=None, depth=None,
               force=False, fetch=False, clean=True skip_changes=False)
```

with optional arguments:

- `*names`: optional list of dependency source or group names to filter on
- `root`: specifies the path to the root working tree
- `depth`: number of levels of dependencies to traverse
- `force`: indicates uncommitted changes can be overwritten and
           script errors can be ignored
- `fetch`: indicates the latest branches should always be fetched
- `clean`: indicates untracked files should be deleted from dependencies
- `skip_changes`: indicates dependencies with uncommitted changes should be skipped

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by calling:

```python
gitman.update(*names, root=None, depth=None, recurse=False,
              force=False, clean=True, lock=None, skip_changes=False)
```

with optional arguments:

- `*names`: optional list of dependency source or group names to filter on
- `root`: specifies the path to the root working tree
- `depth`: number of levels of dependencies to traverse
- `recurse`: indicates nested dependencies should also be updated
- `force`: indicates uncommitted changes can be overwritten and
           script errors can be ignored
- `clean`: indicates untracked files should be deleted from dependencies
- `lock`: indicates updated dependency versions should be recorded
- `skip_changes`: indicates dependencies with uncommitted changes should be skipped

## List

To display the currently checked out dependencies, call:

```python
gitman.list(root=None, depth=None, allow_dirty=True)
```

with optional arguments:

- `root`: specifies the path to the root working tree
- `depth`: number of levels of dependencies to traverse
- `allow_dirty`: causes uncommitted changes to be ignored

## Lock

To record the exact versions of currently checked out dependencies, call:

```python
gitman.lock(*names, root=None)
```

with optional arguments:

- `*names`: optional list of dependency source or group names to filter on
- `root`: specifies the path to the root working tree

## Uninstall

To delete all dependencies, call:

```python
gitman.uninstall(root=None, force=False, keep_location=False)
```

with optional arguments:

- `root`: specifies the path to the root working tree
- `force`: indicates uncommitted changes can be overwritten
- `keep_location`: indicates that the top level folder should be kept
