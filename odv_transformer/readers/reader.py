#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 09:17

@author: johannes
"""
from abc import ABC


class ReaderBase(ABC):
    """Base Reader."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    def get(self, item):
        """Return value for "item"."""
        if item in self.__dict__.keys():
            return self.__getattribute__(item)
        else:
            print('Warning! Can´t find attribute: %s' % item)
            return 'None'

    def load(self, *args, **kwargs):
        """Load."""
        raise NotImplementedError

    def read_element(self, *args, **kwargs):
        """Read."""
        raise NotImplementedError

    @staticmethod
    def eliminate_empty_rows(df):
        """Eliminate empty rows of the given dataframe."""
        return df.loc[df.apply(any, axis=1), :].reset_index(drop=True)
