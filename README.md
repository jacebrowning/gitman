Unix: [![Build Status](https://travis-ci.org/jacebrowning/gitman.svg?branch=develop)](https://travis-ci.org/jacebrowning/gitman) Windows: [![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/gitman/develop.svg)](https://ci.appveyor.com/project/jacebrowning/gitman)<br>Metrics: [![Coverage Status](https://img.shields.io/coveralls/jacebrowning/gitman/develop.svg)](https://coveralls.io/r/jacebrowning/gitman) [![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/gitman.svg)](https://scrutinizer-ci.com/g/jacebrowning/gitman/?branch=develop)<br>Usage: [![PyPI Version](https://img.shields.io/pypi/v/GitMan.svg)](https://pypi.python.org/pypi/GitMan) [![PyPI Downloads](https://img.shields.io/pypi/dm/gitman.svg)](https://pypi.python.org/pypi/GitMan)

# Overview

GitMan is a language-agnostic "dependency manager" using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

![demo](https://raw.githubusercontent.com/jacebrowning/gitman/develop/docs/demo.gif)

# Setup

## Requirements

* Python 3.5+
* Git 2.8+ (with [stored credentials](http://gitman.readthedocs.io/en/latest/setup/git/))

## Installation

Install GitMan with pip:

```sh
$ pip install gitman
```

or directly from the source code:

```sh
$ git clone https://github.com/jacebrowning/gitman.git
$ cd gitman
$ python setup.py install
```

## Setup

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
  - chmod a+x truffleHog.py
```

Ignore the dependency storage location:

```sh
$ echo vendor/gitman >> .gitignore
```

# Usage

See the available commands:

```sh
$ gitman --help
```

## Updating Dependencies

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

* all or part of a commit SHA: `123def`
* a tag: `v1.0`
* a branch: `master`
* a `rev-parse` date: `'develop@{2015-06-18 10:30:59}'`

## Restoring Previous Versions

Display the specific revisions that are currently installed:

```sh
$ gitman list
```

Reinstall these specific versions at a later time:

```sh
$ gitman install
```

## Deleting Dependencies

Remove all installed dependencies:

```sh
$ gitman uninstall
```
