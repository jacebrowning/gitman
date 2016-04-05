# Git Plugin

`gitman` offers a simplified version of the [command-line interface](cli.md) in the form of a plugin for Git.

## Install

To clone/checkout the specified dependencies, run:

```sh
git deps
```

Delete all untracked files in dependencies by instead running:

```sh
git deps --clean
```

Git will exit with an error if there are any uncommitted changes in dependencies. To overwrite all changes, run:

```sh
git deps --force
```

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by running:

```sh
git deps --update
```

This will also record the exact versions that were checked out. Disable this behavior by instead running:

```sh
git deps --update --no-lock
```

Or, to additionally get the latest versions of all nested dependencies, run:

```sh
git deps --update --all
```

To restore the exact versions previously checked out, run:

```sh
git deps
```

## List

To display the currently checked out dependencies, run:

```sh
git deps --list
```

## Uninstall

To delete all dependencies, run:

```sh
git deps --uninstall
```

If any dependencies contain uncommitted changes, instead run:

```sh
git deps --uninstall --force
```
