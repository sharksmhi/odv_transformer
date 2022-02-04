#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 09:17

@author: johannes
"""
from abc import ABC
import pandas as pd
from odv_transformer.readers.reader import ReaderBase


class PandasTxtReader(ReaderBase, ABC):
    """Read txt/csv files with pandas."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__()
        for key, item in kwargs.items():
            setattr(self, key, item)

    def get(self, item):
        """Return value for "item"."""
        if item in self.__dict__.keys():
            return self.__getattribute__(item)
        else:
            print('Warning! Can´t find attribute: %s' % item)
            return 'None'

    @staticmethod
    def read(*args, **kwargs):
        """Return data from pd.read_csv()."""
        return pd.read_csv(*args, **kwargs).fillna('')
