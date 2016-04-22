[![Build Status](https://travis-ci.org/jacebrowning/gitman.svg?branch=develop)](https://travis-ci.org/jacebrowning/gitman)
[![Coverage Status](https://coveralls.io/repos/github/jacebrowning/gitman/badge.svg?branch=develop)](https://coveralls.io/github/jacebrowning/gitman?branch=develop)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/gitman.svg)](https://scrutinizer-ci.com/g/jacebrowning/gitman/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/GitMan.svg)](https://pypi.python.org/pypi/GitMan)
[![PyPI Downloads](http://img.shields.io/pypi/dm/GitMan.svg)](https://pypi.python.org/pypi/GitMan)

# Getting Started

GitMan is a language-agnostic "dependency manager" using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

## Requirements

* Python 3.5+
* Git 1.8+ (with [stored credentials](http://git-dependency-manager.info/setup/git/))
* Unix shell (or Cygwin/MinGW/etc. on Windows)

## Installation

GitMan can be installed with pip:

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

Create a configuration file (`gitman.yml` or `.gitman.yml`) in the root of your working tree:

```yaml
location: vendor
sources:
- name: framework
  repo: https://github.com/kstenerud/iOS-Universal-Framework
  rev: Mk5-end-of-life
- name: coverage
  repo: https://github.com/jonreid/XcodeCoverage
  rev: master
  link: Tools/XcodeCoverage
```

Ignore the dependency storage location:

```sh
$ echo vendor >> .gitignore
```

# Basic Usage

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

1. create a working tree at _root_/`location`/`name`
2. fetch from `repo` and checkout the specified `rev`
3. symbolically link each `location`/`name` from _root_/`link` (if specified)
4. repeat for all nested working trees containing a configuration file
5. record the actual commit SHAs that were checked out (with `--lock` option)

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

# Advanced Options

See the full documentation at [git-dependency-manager.info](http://git-dependency-manager.info/interfaces/cli/).
