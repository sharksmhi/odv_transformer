#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
import pandas as pd
from pathlib import Path
from odv_transformer.readers.zip import SharkzipReader
from odv_transformer.utils import decmin_to_decdeg


class PhysicalChemicalArchiveReader(SharkzipReader):
    """Reader for the PhysicalChemical datatype according to archive format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        for key, item in kwargs.items():
            setattr(self, key, item)
        self.arguments = list(args)
        self.files = {}


    def read_element(self, *args, **kwargs):
        """Read data element.

        Reading excel sheet into pandas.Dataframe.
        """
        df = self._read_file(*args, **kwargs)
        if type(df) == pd.DataFrame:
            if 'LATIT' in df:
                df['LATIT_DD'] = df['LATIT'].apply(decmin_to_decdeg)
            if 'LONGI' in df:
                df['LONGI_DD'] = df['LONGI'].apply(decmin_to_decdeg)
        return df


