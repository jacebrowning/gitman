GDM
===

A very basic language-agnostic "dependency manager" using Git.

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
* OSX/Linux (i.e. a decent shell for Git)

Optional
--------

* A platform capable of creating symbolic links

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

Basic Usage
===========

After installation:

```
$ python3
>>> import gdm
>>> gdm.__version__
```

GDM doesn't do anything yet.

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
