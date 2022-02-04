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
