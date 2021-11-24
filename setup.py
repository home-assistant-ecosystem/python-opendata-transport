#!/usr/bin/env python3
"""Setup for the Transport OpenData wrapper."""
import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="python_opendata_transport",
    version="0.3.0",
    description="Python API for interacting with transport.opendata.ch.",
    long_description=long_description,
    url="https://github.com/home-assistant-ecosystem/python-opendata-transport",
    download_url="https://github.com/home-assistant-ecosystem/python-opendata-transport/releases",
    author="Fabian Affolter",
    author_email="fabian@affolter-engineering.ch",
    license="MIT",
    install_requires=[
        "aiohttp>=3.7.4,<4",
        "urllib3",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
    ],
)
