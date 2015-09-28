[![Build Status](https://travis-ci.org/jacebrowning/gdm.svg?branch=develop)](https://travis-ci.org/jacebrowning/gdm)
[![Coverage Status](http://img.shields.io/coveralls/jacebrowning/gdm/master.svg)](https://coveralls.io/r/jacebrowning/gdm)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/gdm.svg)](https://scrutinizer-ci.com/g/jacebrowning/gdm/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/GDM.svg)](https://pypi.python.org/pypi/GDM)
[![PyPI Downloads](http://img.shields.io/pypi/dm/GDM.svg)](https://pypi.python.org/pypi/GDM)

Getting Started
===============

Requirements
------------

* Python 3.3+
* Latest version of Git (with [stored credentials](http://stackoverflow.com/questions/7773181))
* OSX/Linux (with a decent shell for Git)

Installation
------------

GDM can be installed with pip:

```
$ pip3 install gdm
```

or directly from the source code:

```
$ git clone https://github.com/jacebrowning/gdm.git
$ cd gdm
$ python3 setup.py install
```

Setup
-----

Create a GDM configuration file (`gdm.yml` or `.gdm.yml`) in the root of your working tree:

```yaml
location: .gdm
sources:
- repo: https://github.com/kstenerud/iOS-Universal-Framework
  dir: framework
  rev: Mk5-end-of-life
- repo: https://github.com/jonreid/XcodeCoverage
  dir: coverage
  rev: master
  link: Tools/XcodeCoverage
```

Ignore GDM's dependency storage location:

```
$ echo .gdm >> .gitignore
```

Basic Usage
===========

See the available commands:

```
$ gdm --help
```

Updating Dependencies
---------------------

Get the latest versions of all dependencies:

```
$ gdm update
```

which will essentially:

1. create a working tree at _root_/`location`/`dir`
2. fetch from `repo` and checkout the specified `rev`
3. symbolically link each `location`/`dir` from _root_/`link` (optional)
4. repeat for all nested working trees containing a configuration file
5. record the actual commit SHAs that were checked out

where `rev` can be:

* all or part of a commit SHA: `123def`
* a tag: `v1.0`
* a branch: `master`
* a `rev-parse` date: `'develop@{2015-06-18 10:30:59}'`

Restoring Previous Versions
---------------------------

Display the specific revisions that are currently installed:

```
$ gdm list
```

Reinstall these specific versions at a later time:

```
$ gdm install
```

Deleting Dependencies
---------------------

Remove all installed dependencies:

```
$ gdm uninstall
```
