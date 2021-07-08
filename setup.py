#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='LiteCache',
    version='1.20210708.0',
    description='A Python SQLite-backed key-value cache with data ttl',
    author='Colin Grady',
    author_email='colin@grady.us',
    url='https://github.com/colingrady/LiteCache',
    python_requires='>=3.7',
    packages=find_packages(include='litecache.*')
)
