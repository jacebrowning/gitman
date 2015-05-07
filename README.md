[![Build Status](http://img.shields.io/travis/jacebrowning/gdm/master.svg)](https://travis-ci.org/jacebrowning/gdm)
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

Get the specified versions of all dependencies:

```
$ gdm install
```

which will essentially:

1. create a working tree at _root_/`location`/`dir`
2. fetch from `repo` and checkout the specified `rev`
3. symbolicly link each `location`/`dir` from _root_/`link` (optional)
4. repeat for all nested working trees containing a configuration file

To display the specific versions installed:

```
$ gdm list
```

To remove all installed dependencies:

```
$ gdm uninstall
```
