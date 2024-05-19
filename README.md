## Overview

Gitman is a language-agnostic dependency manager using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

[![Demo](https://raw.githubusercontent.com/jacebrowning/gitman/main/docs/demo.gif)](https://asciinema.org/a/3DLos4HIU84P0AfFlZMYcgPus)

[![Linux Build](https://img.shields.io/github/actions/workflow/status/jacebrowning/gitman/main.yml?branch=main&label=linux)](https://github.com/jacebrowning/gitman/actions)
[![Windows Build](https://img.shields.io/appveyor/ci/jacebrowning/gitman/main.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/gitman)
[![Code Coverage](https://img.shields.io/codecov/c/github/jacebrowning/gitman)
](https://codecov.io/gh/jacebrowning/gitman)
[![Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/gitman.svg?label=quality)](https://scrutinizer-ci.com/g/jacebrowning/gitman/?branch=main)
[![PyPI License](https://img.shields.io/pypi/l/gitman.svg)](https://pypi.org/project/gitman)
[![PyPI Version](https://img.shields.io/pypi/v/gitman.svg?label=version)](https://pypi.org/project/gitman)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gitman.svg?color=orange)](https://pypistats.org/packages/gitman)

## Setup

### Requirements

- Python 3.8+
- Git 2.8+ (with [stored credentials](http://gitman.readthedocs.io/en/latest/setup/git/))

### Installation

Install this tool globally with [pipx](https://pipxproject.github.io/pipx/) (or pip):

```sh
$ pipx install gitman
```
or add it to your [Poetry](https://python-poetry.org/docs/) project:

```sh
$ poetry add gitman
```

### Configuration

Generate a sample config file:

```sh
$ gitman init
```

or manually create one (`gitman.yml` or `.gitman.yml`) in the root of your working tree:

```yaml
location: vendor/gitman

sources:
  - repo: "https://github.com/kstenerud/iOS-Universal-Framework"
    name: framework
    rev: Mk5-end-of-life
  - repo: "https://github.com/jonreid/XcodeCoverage"
    name: coverage
    links:
      - target: Tools/XcodeCoverage
  - repo: "https://github.com/dxa4481/truffleHog"
    name: trufflehog
    rev: master
    scripts:
      - chmod a+x truffleHog/truffleHog.py
  - repo: "https://github.com/FortAwesome/Font-Awesome"
    name: fontawesome
    rev: master
    sparse_paths:
      - "webfonts/*"
  - repo: "https://github.com/google/material-design-icons"
    name: material-design-icons
    rev: master

groups:
  - name: code
    members:
      - framework
      - trufflehog
  - name: resources
    members:
      - fontawesome
      - material-design-icons

default_group: code
```

Ignore the dependency storage location:

```sh
$ echo vendor/gitman >> .gitignore
```

## Usage

See the available commands:

```sh
$ gitman --help
```

### Updating Dependencies

Get the latest versions of all dependencies:

```sh
$ gitman update
```

which will essentially:

1. Create a working tree at `<root>`/`<location>`/`<name>`
2. Fetch from `repo` and checkout the specified `rev`
3. Symbolically link each `<location>`/`<name>` from `<root>`/`<link>` (if specified)
4. Repeat for all nested working trees containing a config file
5. Record the actual commit SHAs that were checked out (with `--lock` option)
6. Run optional post-install scripts for each dependency

where `rev` can be:

- all or part of a commit SHA: `123def`
- a tag: `v1.0`
- a branch: `main`
- a `rev-parse` date: `'main@{2015-06-18 10:30:59}'`

Alternatively, get the latest versions of specific dependencies:

```sh
$ gitman update framework
```

or named groups:

```sh
$ gitman update resources
```

### Restoring Previous Versions

Display the versions that are currently installed:

```sh
$ gitman list
```

Reinstall these specific versions at a later time:

```sh
$ gitman install
```

### Deleting Dependencies

Remove all installed dependencies:

```sh
$ gitman uninstall
```

## Resources

- [Source code](https://github.com/jacebrowning/gitman)
- [Issue tracker](https://github.com/jacebrowning/gitman/issues)
- [Release history](https://github.com/jacebrowning/gitman/blob/main/CHANGELOG.md)
