## Overview

GitMan is a language-agnostic dependency manager using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

![demo](https://raw.githubusercontent.com/jacebrowning/gitman/develop/docs/demo.gif)

[![Unix Build Status](https://img.shields.io/travis/jacebrowning/gitman/master.svg?label=unix)](https://travis-ci.org/jacebrowning/gitman)
[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/gitman/master.svg?label=window)](https://ci.appveyor.com/project/jacebrowning/gitman)
[![Coverage Status](https://img.shields.io/coveralls/jacebrowning/gitman/master.svg)](https://coveralls.io/r/jacebrowning/gitman)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/gitman.svg)](https://scrutinizer-ci.com/g/jacebrowning/gitman/?branch=master)
[![PyPI Version](https://img.shields.io/pypi/v/GitMan.svg)](https://pypi.org/project/GitMan)
[![PyPI License](https://img.shields.io/pypi/l/GitMan.svg)](https://pypi.org/project/GitMan)

## Setup

### Requirements

- Python 3.6+
- Git 2.8+ (with [stored credentials](http://gitman.readthedocs.io/en/latest/setup/git/))

### Installation

Install this tool globally:

```sh
$ pip install gitman
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

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
  - name: framework
    repo: https://github.com/kstenerud/iOS-Universal-Framework
    rev: Mk5-end-of-life
  - name: coverage
    repo: https://github.com/jonreid/XcodeCoverage
    rev: master
    link: Tools/XcodeCoverage
  - name: trufflehog
    repo: https://github.com/dxa4481/truffleHog
    rev: master
    scripts:
      - chmod a+x truffleHog/truffleHog.py
  - name: fontawesome
    repo: https://github.com/FortAwesome/Font-Awesome
    sparse_paths:
      - "webfonts/*"
    rev: master
  - name: material-design-icons
    repo: https://github.com/google/material-design-icons.git
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
- a branch: `master`
- a `rev-parse` date: `'develop@{2015-06-18 10:30:59}'`

Alternatively get the latest versions of certain dependencies or even dependency groups:

- Update a single repository

```sh
$ gitman update framework
```

- Update a dependency group

```sh
$ gitman update resources
```

### Restoring Previous Versions

Display the specific revisions that are currently installed:

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
