# Git Dependency Manager

GitMan is a language-agnostic "dependency manager" using Git. It aims to serve as a submodules replacement and provides advanced options for managing versions of nested Git repositories.

## Requirements

* Python 3.4+
* Latest version of Git (with [stored credentials](setup/git/#stored-credentials))
* OSX/Linux (with a decent shell for Git)

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
- repo: https://github.com/kstenerud/iOS-Universal-Framework
  dir: framework
  rev: Mk5-end-of-life
- repo: https://github.com/jonreid/XcodeCoverage
  dir: coverage
  rev: master
  link: Tools/XcodeCoverage
```

Ignore the dependency storage location:

```sh
$ echo vendor >> .gitignore
```

## Basic Usage

Get all dependencies:

```sh
$ gitman install
```

which will essentially:

1. create a working tree at _root_/`location`/`dir`
2. fetch from `repo` and checkout the specified `rev`
3. symbolically link each `location`/`dir` from _root_/`link` (if specified)
4. repeat for all nested working trees containing a configuration file

where `rev` can be:

* all or part of a commit SHA: `123def`
* a tag: `v1.0`
* a branch: `master`
* a `rev-parse` date: `'develop@{2015-06-18 10:30:59}'`
