#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:00

@author: johannes
"""
from pathlib import Path
from collections import Mapping


def get_base_folder():
    """Return the base folder of ODV-transformer."""
    return Path(__file__).parent


def recursive_dict_update(d: dict, u: dict) -> dict:
    """Recursive dictionary update.

    Copied from:
        http://stackoverflow.com/questions/3232943/update-
        value-of-a-nested-dictionary-of-varying-depth
        via satpy
    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

