#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:00

@author: johannes
"""
from pathlib import Path


def get_base_folder():
    """Return the base folder of ODV-transformer."""
    return Path(__file__).parent
