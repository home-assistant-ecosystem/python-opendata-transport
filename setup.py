#!/usr/bin/env python3

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist upload')
    sys.exit()

setup(
    name='python_opendata_transport',
    version='0.0.1',
    description='Python API for interacting with transport.opendata.ch.',
    url='https://github.com/fabaff/python-opendata-transport',
    download_url='https://github.com/fabaff/python-opendata-transport/releases',
    author='Fabian Affolter',
    author_email='fabian@affolter-engineering.ch',
    license='MIT',
    install_requires=['requests>=2.0', 'pytz'],
    packages=['opendata_transport'],
    zip_safe=True,
)
