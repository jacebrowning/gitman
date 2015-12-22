# Command-line Interface

After setting up GDM with a [configuration file](../index.md#setup), various commands can be run to manage these Git-controlled source dependencies.

## Install

To clone/checkout the specified dependencies, run:

```sh
gdm install
```

or filter the dependency list by directory name:

```sh
gdm install <dir1> <dir2> <etc.>
```

or limit the traversal of nested dependencies:

```sh
gdm install --depth=<count>
```

Delete all untracked files in dependencies by instead running:

```sh
gdm install --clean
```

The program will exit with an error if there are any uncommitted changes in dependencies. To overwrite all changes, run:

```sh
gdm install --force
```

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by running:

```sh
gdm update
```

or filter the dependency list by directory name:

```sh
gdm update <dir1> <dir2> <etc.>
```

or limit the traversal of nested dependencies:

```sh
gdm update --depth=<count>
```

This will also record the exact versions of any previously locked dependencies. Disable this behavior by instead running:

```sh
gdm update --no-lock
```

or to additionally get the latest versions of all nested dependencies, run:

```sh
gdm update --all
```

## List

To display the currently checked out dependencies, run:

```sh
gdm list
```

or exit with an error if there are any uncommitted changes:

```sh
gdm list --no-dirty
```

## Lock

To manually record the exact version of each dependency, run:

```sh
gdm lock
```

or lock down specific dependencies:

```sh
gdm lock <dir1> <dir2> <etc.>
```

This can be combined with updating dependencies by running:

```sh
gdm update --lock
```

To restore the exact versions previously checked out, run:

```sh
gdm install
```

## Uninstall

To delete all source dependencies, run:

```sh
gdm uninstall
```

If any dependencies contain uncommitted changes, instead run:

```sh
gdm uninstall --force
```
