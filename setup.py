#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'obj2xml',
    version = '1.0.1',
    description = 'Convenient XML creation using objects',
    license = 'BSD',
    author = 'Adam Griffiths',
    author_email = 'adam.lw.griffiths@gmail.com',
    url = 'https://github.com/adamlwgriffiths/obj2xml',
    install_requires = ['pydict2xml'],
    platforms = ['any'],
    test_suite = 'tests',
    packages = ['obj2xml'],
    classifiers = [
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML',
    ],
)