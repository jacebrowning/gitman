# Command-line Interface

After setting up `gitman` with a [configuration file](../index.md#setup), various commands can be run to manage these Git-controlled source dependencies.

## Install

To clone/checkout the specified dependencies, run:

```sh
gitman install
```

or filter the dependency list by directory name:

```sh
gitman install <name1> <name2> <etc.>
```

or limit the traversal of nested dependencies:

```sh
gitman install --depth=<count>
```

It will leave untracked files alone. To delete them, run:

```sh
gitman install --clean
```

It will only fetch from the repository if needed. To always fetch, run:

```sh
gitman install --fetch
```

It will exit with an error if there are any uncommitted changes in dependencies. To overwrite all changes, run:

```sh
gitman install --force
```

## Update

If any of the dependencies track a branch (rather than a specific commit), the current upstream version of that branch can be checked out by running:

```sh
gitman update
```

or filter the dependency list by directory name:

```sh
gitman update <name1> <name2> <etc.>
```

or limit the traversal of nested dependencies:

```sh
gitman update --depth=<count>
```

This will also record the exact versions of any previously locked dependencies. Disable this behavior by instead running:

```sh
gitman update --no-lock
```

or to additionally get the latest versions of all nested dependencies, run:

```sh
gitman update --all
```

## List

To display the currently checked out dependencies, run:

```sh
gitman list
```

or exit with an error if there are any uncommitted changes:

```sh
gitman list --no-dirty
```

The `list` command will also record versions in the log file.

## Lock

To manually record the exact version of each dependency, run:

```sh
gitman lock
```

or lock down specific dependencies:

```sh
gitman lock <name1> <name2> <etc.>
```

This can be combined with updating dependencies by running:

```sh
gitman update --lock
```

To restore the exact versions previously checked out, run:

```sh
gitman install
```

## Uninstall

To delete all dependencies, run:

```sh
gitman uninstall
```

If any dependencies contain uncommitted changes, instead run:

```sh
gitman uninstall --force
```

## Show

To display the path to the dependency storage location:

```sh
gitman show
```

To display the path to a dependency:

```sh
gitman show <name>
```

To display the path to the configuration file:

```sh
gitman show --config
```

To display the path to the log file:

```sh
gitman show --log
```

## Edit

To open the existing configuration file:

```sh
gitman edit
```
