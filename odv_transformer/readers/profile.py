#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
import pandas as pd
from pathlib import Path
from odv_transformer.readers.reader import ReaderBase
from ctdpy.core.session import Session as ctd_session
from ctdpy.core.utils import generate_filepaths


class ProfileReader(ReaderBase):
    """Reader for the Profile datatype according to standard ODV format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__()
        self.mapper = None
        for key, item in kwargs.items():
            setattr(self, key, item)
        self.arguments = list(args)
        self.files = {}

    def load(self, *args, **kwargs):
        """Activate files."""
        self._activate_files(*args, **kwargs)

    def read_element(self, *args, **kwargs):
        """Read data element.

        Reading excel sheet into pandas.Dataframe.
        """
        session = ctd_session(filepaths=self.files.values(),
                              reader='ctd_stdfmt')
        datasets = session.read()
        datasets = datasets[0]
        df = pd.DataFrame()
        for item in datasets.values():
            self._set_format(item)
            df = df.append(item['data'], ignore_index=True)
        return df

    def _set_format(self, dset):
        """Add metadata to dataframe."""
        mdict = {
            v[1]: v[2] for v in dset['metadata'][dset[
                'metadata'].str.startswith('//METADATA;')].str.split(';')
        }
        for c in ('MYEAR', 'SHIPC', 'CRUISE_NO',
                  'SERNO', 'SDATE', 'STIME', 'WADEP'):
            dset['data'][c] = mdict.get(c, '')
        dset['data'] = dset['data'].rename(columns=self.mapper)

    def _activate_files(self, *args, **kwargs):
        """Set folder paths to self.files."""
        folder_path = Path(args[0]) if type(args) == tuple else Path(args)
        if not folder_path.exists():
            raise FileNotFoundError(
                f'Could not find the given directory {folder_path=}'
            )
        data_path = Path(f"{folder_path}/data") #Path(f"{folder_path}/data")
        if not data_path.exists():
            raise FileNotFoundError(
                f'{data_path=} does not exist'
            )

        for fid in generate_filepaths(str(data_path), endswith='.txt'):
            fid = Path(fid)
            self.files.setdefault(fid.name, fid)
