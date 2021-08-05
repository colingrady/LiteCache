#!/usr/bin/env python

from setuptools import setup

from litecache import __version__ as lib_version


setup(
    name='litecache',
    version=lib_version,
    description='A Python SQLite-backed key-value cache with data TTL',
    author='Colin Grady',
    author_email='colin@grady.us',
    url='https://github.com/colingrady/LiteCache',
    python_requires='>=3.7',
    py_modules=['litecache'],
)
