#!/usr/bin/python3
import os
from setuptools import find_packages, setup, Command
import msquared

# Package meta-data.
NAME = "msquared"
DESCRIPTION = "A makefile generator."
URL = "https://github.com/pmarathe25/MSquared"
EMAIL = "pmarathe25@gmail.com"
AUTHOR = "Pranav Marathe"
REQUIRES_PYTHON = ">=3.6.0"

# What packages are required for this module to be executed?
REQUIRED = [
]

curdir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with open(os.path.join(curdir, "README.md")) as f:
    long_description = '\n' + f.read()

setup(
    name=NAME,
    version=msquared.__version__,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    zip_safe=True,
    packages=["msquared"],
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
