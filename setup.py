#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-04 15:16

@author: johannes
"""
import os
import setuptools


requirements = []
with open('requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())

NAME = 'odv_transformer'
VERSION = '0.0.2'
with open("README.md", "r", encoding="utf-8") as fh:
    README = fh.read()

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Johannes Johansson",
    author_email="nodc@smhi.se",
    description="Package to transform data to ODV-ICES-delivery format.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sharksmhi/odv_transformer",
    packages=setuptools.find_packages(),
    package_data={
        'odv_transformer': [
            os.path.join('etc', '*.json'),
            os.path.join('etc', '*.yaml'),
            os.path.join('etc', 'readers', '*.yaml'),
            os.path.join('etc', 'writers', '*.yaml'),
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=requirements,
)
