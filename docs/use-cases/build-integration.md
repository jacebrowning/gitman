# Build System Integration

GitMan can be invoked from your build system or continuous integration environment. It provides a convenient way to access its internal file and directory paths using the [`show`](../interfaces/cli.md#show) command.

## Makefile

The following example shows one way you might want to call `gitman` from within a Makefile:

```makefile
.PHONY: all
all: depends

.PHONY: depends
depends: $(shell gitman show --log)
$(shell gitman show --log): $(shell gitman show --config)
	gitman install
	make -C $(shell gitman show lib_foo) configure all install
	make -C $(shell gitman show lib_bar) configure all install
	gitman list

.PHONY: clean
clean:
  gitman uninstall
```

using a configuration file similar to:

```yaml
location: vendor
sources:
- name: lib_foo
  repo: https://github.com/example/lib_foo
  rev: develop
- name: lib_bar
  repo: https://github.com/example/lib_bar
  rev: master
sources_locked:
- name: lib_foo
  repo: https://github.com/example/lib_foo
  rev: 73cb3668d4c9c3388fb21de16c9c3f6217cc0e1c
- name: lib_bar
  repo: https://github.com/example/lib_bar
  rev: 560ea99953a4b3e393e170e07895d14904eb032c
```

## Workflow

Running `make depends` performs the following actions:

1. Check the modification times of the configuration and log files
2. If the configuration file is newer, continue
3. Install the locked dependency versions
4. Run `make` inside of each dependency's folder
5. Update the log file with the current versions of all dependencies

To update your dependencies:

1. Run `gitman update`
2. Run `make depends`
3. If the new build passes your tests, commit the new configuration file
