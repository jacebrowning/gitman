# Command-line Interface

After setting up GDM with a [configuration file](../index.md#setup), various commands can be run to manage these Git-controlled source dependencies.

## Install

To clone/checkout the specified dependencies, run:

```sh
gdm install
```

Delete all untracked files in dependencies by instead running:

```sh
gdm install --clean
```

GDM will exit with an error if there are any uncommitted changes in dependencies. To overwrite all changes, run:

```sh
gdm install --force
```

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by running:

```sh
gdm update
```

This will also record the exact versions that were checked out. Disable this behavior by instead running:

```sh
gdm update --no-lock
```

Or, to additionally get the latest versions of all nested dependencies, run:

```sh
gdm update --all
```

To restore the exact versions previously checked out, run:

```sh
gdm install
```

## List

To display the currently checked out dependencies, run:

```sh
gdm list
```

Exit with an error if there are any uncommitted changes by instead running:

```sh
gdm list --no-dirty
```

## Uninstall

To delete all source dependencies:

```sh
gdm uninstall
```

If any dependencies contain uncommitted changes, instead run:

```sh
gdm uninstall --force
```
