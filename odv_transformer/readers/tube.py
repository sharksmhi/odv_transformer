#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:23

@author: johannes
"""
import pandas as pd
from odv_transformer.readers.zip import SharkzipReader


def adjust_cruise_number(cruise):
    """Fill up with zeros."""
    return cruise.zfill(2) if cruise else cruise


class TubeChlReader(SharkzipReader):
    """Reader for the SHARK chl tube sampling datatype."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.mapper = None
        super().__init__(*args, **kwargs)

    def read_element(self, *args, **kwargs):
        """Read data element.

        Reading excel sheet into pandas.Dataframe.
        """
        df = self._read_file(*args, **kwargs)
        if type(df) == pd.DataFrame:
            df.rename(columns=self.mapper, inplace=True)
            for col in {'LATIT_DD', 'LONGI_DD'}:
                if col in df:
                    df[col] = df[col].str.replace(' ', '')
            df = df[list(self.mapper.values())]
            df['SERNO'] = df['SERNO'].str.zfill(4)
            df['CRUISE_NO'] = df['CRUISE_NO'].apply(adjust_cruise_number)

        return df
