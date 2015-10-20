# Package API

All of the [command-line interface](cli.md) functionality is available from the Python package by importing `gdm`.

## Install

To clone/checkout the specified dependencies, call:

```python
gdm.install(root=None, force=False, clean=True)
```

where optional arguments:

- `root`: specifies the path to the root working tree
- `force`: indicates that uncommitted changes can be overwritten
- `clean`: causes all untracked files to be deleted from dependencies

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by calling:

```python
gdm.update(root=None, recurse=False, force=False, clean=True, lock=True)
```

where optional arguments:

- `root`: specifies the path to the root working tree
- `recurse`: indicates that nested dependencies should also be updated
- `force`: indicates that uncommitted changes can be overwritten
- `clean`: causes all untracked files to be deleted from dependencies
- `lock`: causes the actual dependency versions to be recorded for future installs

## List

To display the currently checked out dependencies, call:

```python
gdm.list(root=None, allow_dirty=True)
```

where optional arguments:

- `root`: specifies the path to the root working tree
- `allow_dirty`: causes uncommitted changes to be ignored

## Uninstall

To delete all source dependencies, call:

```python
gdm.uninstall(root=None, force=False)
```

where optional arguments:

- `root`: specifies the path to the root working tree
- `force`: indicates that uncommitted changes can be overwritten
