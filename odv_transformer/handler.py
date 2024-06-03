#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 09:34

@author: johannes
"""
from abc import ABC
import pandas as pd


def get_key(x):
    """Return key.

    According to standard NODC-PhyChe serie format (YEAR_SHIPC_SERNO).
    """
    return '_'.join(x)


def get_timestamp(x):
    """Return timestring (UTC)."""
    return 'T'.join(x) + 'Z'
    # return pd.Timestamp('T'.join(x), tz='UTC').strftime('%Y-%m-%dT%H:%MZ')


def comma_2_dot(x):
    """Return column without commas."""
    return x.replace(',', '.')


def clean_cruise(x):
    """Return cruise number without leading zeros."""   
    return str(x).lstrip('0')


def get_cruise(x):
    """Return cruise string according to ICES format.

    Format: {YEAR}{SHIPC}{CRUISE_NO}
    """
    return ''.join(x)


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

    def filter_data(self, filters):
        """Remove unwanted data based on given filters.

        Args:
            filters (dict): Contains lists with valid values to keep.
                            Example: {
                                'MYEAR': ['2020', '2022'],
                                'SHIPC': ['77SE']
                            }
        """
        if not filters:
            return

        boolean = True
        for key, item in filters.items():
            if key in self.keys() and isinstance(item, list):
                boolean = boolean & (self[key].isin(item))

        if isinstance(boolean, bool):
            return
        else:
            self.drop(self.index[~boolean], inplace=True)
            self.reset_index(drop=True, inplace=True)

    def convert_formats(self):
        """Convert formats of self."""
        self['STATN'] = self['STATN'].apply(
            comma_2_dot
        )
        self['KEY'] = self[['MYEAR', 'SHIPC', 'SERNO']].apply(
            get_key, axis=1
        )
        self['CRUISE_NO'] = self['CRUISE_NO'].apply(
            clean_cruise
        )
        self['CRUISE_NO'] = self[['MYEAR', 'SHIPC', 'CRUISE_NO']].apply(
            get_cruise, axis=1
        )
        self['TIMESTAMP'] = self[['SDATE', 'STIME']].apply(
            get_timestamp, axis=1
        )

    def delete_empty_columns(self):
        """Delete columns without any data."""
        cols_to_drop = set()
        for key, boolean in self.eq('').all().items():
            if boolean:
                if key.startswith('Q') and key[2:] not in cols_to_drop:
                    # we keep Q-fields if there is data in the data column
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
        if 'DEPH' in self.columns and 'MNDEP' in self.columns:
            cols = ['DEPH', 'MNDEP', 'MXDEP']
        elif 'DEPH' in self.columns:
            cols = ['DEPH']
        else:
            cols = ['MNDEP', 'MXDEP']

        for c in self.quality_flag_columns:
            if c[2:] not in {'DEPH', 'MNDEP', 'MXDEP'}:
                cols.append(c[2:])
        return cols

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

    def append_new_frame(self, name=None, data=None, merge=False, filters=None,
                         **kwargs):
        """Append new Frame-object to self.

        Args:
            name (str): Name of dataset (eg. "data", "analyse_info").
            data (pd.DataFrame): Data
            merge (bool): If True we can assume that standard format handling
                          has already been applied.
            filters (dict): Contains lists with valid values to keep.
            **kwargs:
        """
        if name == 'profile_data':
            for key in list(data):
                data[key]['data'] = Frame(data[key]['data'])
                data[key]['data'].filter_data(filters)
                data[key]['data'].convert_formats()
                data[key]['data'].add_meta_columns()
            self.setdefault(name, data)
        elif name:
            self.setdefault(name, Frame(data))

        if name in 'data' and not merge:
            self[name].filter_data(filters)
            self[name].convert_formats()
            self[name].delete_empty_columns()
            self[name].add_meta_columns()


class MultiDeliveries(dict):
    """Stores multiple data deliveries."""

    def append_new_delivery(self, name=None, data=None, **kwargs):
        """Append new delivery.

        Args:
            name (str): Name of delivery (eg. "SMHI-phytoplankton").
            data (DataFrames-obj): Data incl. all elements of delivery.
            **kwargs:
        """
        if name:
            self.setdefault(name, data)

    def merge_deliveries(self, name=None, deliveries=None):
        """Merge multiple deliveries.

        Args:
            name (str): New name for the merged dataset.
            deliveries (iterable): Name of deliveries.
        """
        deliveries = deliveries or []

        if name and len(deliveries) > 1:
            merge = self[deliveries[0]]['data']
            for delivery_name in deliveries[1:]:
                merge = merge.append(self[delivery_name]['data'],
                                     ignore_index=True)

            dfs = DataFrames(data_type='merged_dataset', name=name)
            dfs.append_new_frame(name='data', data=merge, merge=True)
            self.setdefault(name, dfs)

    def drop_delivery(self, name=None):
        """Delete delivery."""
        if name in self:
            self.pop(name)
