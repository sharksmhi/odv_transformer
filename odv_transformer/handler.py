#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 09:34

@author: johannes
"""
from abc import ABC
import pandas as pd
from odv_transformer.utils import decmin_to_decdeg


def get_key(x):
    """Return key.

    According to standard NODC-PhyChe serie format (YEAR_SHIPC_SERNO).
    """
    return '_'.join(x[['MYEAR', 'SHIPC', 'SERNO']])


def get_timestamp(x):
    """Return timestring (UTC)."""
    return pd.Timestamp('T'.join(x[['SDATE', 'STIME']]), tz='UTC').isoformat()


def get_cruise(x):
    """Return cruise string according to ICES format.

    Format: {YEAR}{SHIPC}{CRUISE_NO}
    """
    return ''.join(x[['MYEAR', 'SHIPC', 'CRUISE_NO']])


class Frame(pd.DataFrame, ABC):
    """Stores data from one, and only one, element.

    'Element' is usually an excel sheet or a txt file.
    """

    @property
    def _constructor(self):
        """Construct Frame.

        Constructor for Frame, overrides method in pandas.DataFrame.
        """
        return Frame

    def add_meta_columns(self):
        """Add mandatory metadata columns."""
        self['CUSTODIAN'] = '545'  # SMHI (ICES code)
        self['DISTRIBUTOR'] = '545'  # SMHI (ICES code)
        self['SMTYP'] = ''  # eg. B (BTL), C (CTD)
        self['SMCAT'] = ''  # eg. 30 (BTL-category), 130 (CTD-category)

    def convert_formats(self):
        """Convert formats of self."""
        self['KEY'] = self.apply(get_key, axis=1)
        self['CRUISE_NO'] = self.apply(get_cruise, axis=1)
        self['TIMESTAMP'] = self.apply(get_timestamp, axis=1)
        self['LATIT'] = self['LATIT'].apply(decmin_to_decdeg)
        self['LONGI'] = self['LONGI'].apply(decmin_to_decdeg)

    def delete_empty_columns(self):
        """Delete columns without any data."""
        cols_to_drop = set()
        for key, boolean in self.eq('').all().items():
            if boolean:
                if key.startswith('Q_'):
                    # we keep Q-fields if there is data in the data column
                    if key[2:] not in cols_to_drop:
                        continue
                cols_to_drop.add(key)
        self.drop(columns=cols_to_drop, inplace=True)

    def delete_rows_with_no_data(self):
        """Delete rows without any data."""
        self.replace('', float('nan'), inplace=True)
        self.dropna(
            subset=self.data_columns_incl_flags,
            inplace=True,
            how='all'
        )
        self.replace(float('nan'), '', inplace=True)
        self.reset_index(drop=True, inplace=True)

    @property
    def data_columns(self):
        """Return data columns (not metadata- or quality flag-columns)."""
        return ['DEPH'] + [c[2:] for c in self.quality_flag_columns]

    @property
    def data_columns_incl_flags(self):
        """Return metadata columns."""
        return self.data_columns[1:] + self.quality_flag_columns

    @property
    def meta_columns(self):
        """Return metadata columns."""
        return [c for c in self.columns
                if c not in self.data_columns_incl_flags]

    @property
    def quality_flag_columns(self):
        """Return quality flag columns."""
        return [c for c in self.columns if c.startswith('Q_')]


class DataFrames(dict):
    """Stores information for delivery elements.

    Sheets / files:
        delivery_info
        data
        analyse_info
        sampling_info

    Use element name as key in this dictionary of Frame()-objects.
    """

    def __init__(self, **kwargs):
        """Initialize."""
        super(DataFrames, self).__init__()
        for key, item in kwargs.items():
            setattr(self, key, item)

    def append_new_frame(self, name=None, data=None, **kwargs):
        """Append new Frame-object to self.

        Args:
            name (str): Name of dataset (eg. "data", "analyse_info").
            data (pd.DataFrame): Data
            **kwargs:
        """
        if name:
            self.setdefault(name, Frame(data))
        if name == 'data':
            self[name].convert_formats()
            self[name].delete_empty_columns()
            self[name].add_meta_columns()
            self.divide_on_smtyp(name)
            self[name].delete_rows_with_no_data()
            # self[name].translation()

    def divide_on_smtyp(self, name):
        """Divide dataframe based on sampling type (SMTYP)."""
        df_cdf = None
        ctd_cols = [c for c in self[name].columns if '_CTD' in c]
        if ctd_cols:
            frame_cols = self[name].meta_columns + ctd_cols
            df_cdf = self[name].loc[:, frame_cols].copy()
            df_cdf.rename(
                columns={c: c.replace('_CTD', '') for c in ctd_cols},
                inplace=True
            )
            self[name].drop(columns=ctd_cols, inplace=True)
            df_cdf['SMTYP'] = 'C'
            df_cdf['SMCAT'] = '130'

        self[name].rename(
            columns={c: c.replace('_BTL', '') for c in self[name].columns},
            inplace=True
        )
        self[name]['SMTYP'] = 'B'
        self[name]['SMCAT'] = '30'
        if ctd_cols:
            for c in ctd_cols:
                valid_col = c.replace('_CTD', '')
                if valid_col not in self[name]:
                    self[name][valid_col] = ''

            self[name] = self[name].append(df_cdf, ignore_index=True)


class MultiDeliveries(dict):
    """Stores multiple data deliveries."""

    def append_new_delivery(self, name=None, data=None, **kwargs):
        """Append new delivery.

        Args:
            name (str): Name of delivery (eg. "SMHI-phytoplankton").
            data (DataFrames-obj): Data incl. all elements of delivery.
            **kwargs:
        """
        delivery_name = name
        if delivery_name:
            self.setdefault(delivery_name, data)

    def drop_delivery(self, name=None):
        """Delete delivery."""
        if name in self:
            self.pop(name)
