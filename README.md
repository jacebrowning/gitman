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
* Git (with stored credentials)
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

Create a GDM configuration file in the root of your working tree:

```yaml
location: .gdm
sources:
- repo: https://github.com/kstenerud/iOS-Universal-Framework
  dir: framework
  rev: Mk5-end-of-life
  link: Frameworks/iOS-Universal-Framework
- repo: https://github.com/jonreid/XcodeCoverage
  dir: coverage
  rev: master
  link: Tools/XcodeCoverage
```

Ignore the source location:

```
$ echo .gdm >> .gitignore
```

Basic Usage
===========

Get the specified versions of all dependencies:

```
$ gdm install
```

Remove all installed dependencies:

```
$ gdm uninstall
```

For Contributors
================

Requirements
------------

* Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

```
$ make env
```

Run the tests:

```
$ make test
$ make tests  # includes integration tests
```

Build the documentation:

```
$ make doc
```

Run static analysis:

```
$ make pep8
$ make pep257
$ make pylint
$ make check  # includes all checks
```

Prepare a release:

```
$ make dist  # dry run
$ make upload
```
