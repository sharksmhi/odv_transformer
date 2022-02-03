#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 17:51

@author: johannes
"""
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from odv_transformer.readers import *  # noqa: F401, F403
from odv_transformer.writers import *  # noqa: F401, F403
from odv_transformer.main import Session  # noqa: F401

name = "odv_transformer"
