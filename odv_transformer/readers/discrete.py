#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
import pandas as pd
from pathlib import Path
from odv_transformer.readers.txt import PandasTxtReader
from odv_transformer.utils import decmin_to_decdeg


class PhysicalChemicalArchiveReader(PandasTxtReader):
    """Reader for the PhysicalChemical datatype according to archive format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
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
        df = self._read_file(*args, **kwargs)
        if type(df) == pd.DataFrame:
            if 'LATIT' in df:
                df['LATIT_DD'] = df['LATIT'].apply(decmin_to_decdeg)
            if 'LONGI' in df:
                df['LONGI_DD'] = df['LONGI'].apply(decmin_to_decdeg)
        return df

    def _read_file(self, *args, **kwargs):
        """Read file (element) and return dataframe."""
        fid = args[0] if type(args) == tuple else args
        if fid in self.files:
            if kwargs.get('dtype') == '':
                kwargs['dtype'] = str
            df = self.read(self.files.get(fid), **kwargs)
            df = self.eliminate_empty_rows(df)
        else:
            df = None
            print('File {} not found in delivery'.format(fid))
        return df

    def _activate_files(self, *args, **kwargs):
        """Set folder paths to self.files."""
        folder_path = Path(args[0]) if type(args) == tuple else Path(args)
        if not folder_path.exists:
            raise FileNotFoundError(
                'Could not find the given directory: {}'.format(folder_path)
            )
        if folder_path.name != 'processed_data':
            folder_path = folder_path / 'processed_data'

        for file_name in folder_path.glob('**/*'):
            self.files.setdefault(file_name.name, file_name)
