#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:00

@author: johannes
"""
import numpy as np
from pathlib import Path
from collections import Mapping
from threading import Thread
from decimal import Decimal, ROUND_HALF_UP


def round_value(value: (str, int, float), nr_decimals=2) -> str:
    """Calculate rounded value."""
    return str(Decimal(str(value)).quantize(
        Decimal('%%1.%sf' % nr_decimals % 1),
        rounding=ROUND_HALF_UP)
    )


def decmin_to_decdeg(pos, decimals=4):
    """Convert degrees and decimal minutes into decimal degrees."""
    pos = float(pos)
    output = np.floor(pos / 100.) + (pos % 100) / 60.
    return round_value(output, nr_decimals=decimals)


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


def thread_process(call_function, *args, **kwargs):
    """Thread process.

    Args:
        call_function: function to use
        args: Arguments to call_function
        kwargs: Key word arguments to call_function
    """
    Thread(target=call_function, args=args, kwargs=kwargs).start()
