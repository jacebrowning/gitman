#!/usr/bin/env python

"""Setup script for GitMan."""

import setuptools

from gitman import __project__, __version__, CLI, PLUGIN, DESCRIPTION

import os
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, README is generated on release
CHANGES = open('CHANGES.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description=DESCRIPTION,
    url='http://git-dependency-manager.info',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': [
        CLI + ' = gitman.cli:main',
        'git-' + PLUGIN + ' = gitman.plugin:main',
        # Legacy entry points:
        'gdm = gitman.cli:main',
    ]},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Software Distribution',
    ],

    install_requires=open('requirements.txt').readlines(),
)
