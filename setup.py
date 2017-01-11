#!/usr/bin/env python

"""Setup script for the package."""

import os
import sys

import setuptools


PACKAGE_NAME = 'gitman'
MINIMUM_PYTHON_VERSION = 3, 5


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}.{1}+ is required.".format(*MINIMUM_PYTHON_VERSION))


def read_package_variable(key, filename='__init__.py'):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ', 2)
            if parts[:-1] == [key, '=']:
                return parts[-1].strip("'")
    sys.exit("'{0}' not found in '{1}'".format(key, module_path))


def read_descriptions():
    """Build a description for the project from documentation files."""
    try:
        readme = open("README.rst").read()
        changelog = open("CHANGELOG.rst").read()
    except IOError:
        return "<placeholder>"
    else:
        return readme + '\n' + changelog


check_python_version()

setuptools.setup(
    name=read_package_variable('__project__'),
    version=read_package_variable('__version__'),

    description=read_package_variable('DESCRIPTION'),
    url='https://jacebrowning/gitman',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': [
        read_package_variable('CLI') + ' = gitman.cli:main',
        'git-' + read_package_variable('PLUGIN') + ' = gitman.plugin:main',
        # Legacy entry points:
        'gdm = gitman.cli:main',
    ]},

    long_description=read_descriptions(),
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Software Distribution',
    ],

    install_requires=[
        'YORM~=1.1',
    ],
)
