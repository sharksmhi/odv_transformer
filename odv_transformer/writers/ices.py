#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
from odv_transformer.writers.writer import WriterBase, write_with_numpy


class IcesOdvWriter(WriterBase):
    """Convert NODC format into ICES ODV delivery format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.meta_block_prefix = None
        self.meta_spec = None
        self.data_spec = None
        self.ices_mapping_spec = None
        self.pmap = None
        self.selected_columns = set()
        super().__init__(*args, **kwargs)

    def write(self, file_path, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        self.pmap = pmap
        self._reset_serie()

        df = self.divide_on_smtyp(data['data'])
        df.delete_rows_with_no_data()

        self.add_meta_variables()
        self.add_data_variables(df)
        self.add_ices_mapping(df)
        self.add_data_table(df)

        self._write(file_path)

    def _write(self, fid, **kwargs):
        """Write data to file according to ICES ODV format."""
        print(f'writing to: {fid}')
        write_with_numpy(data=self.data_serie, save_path=fid)

    def _reset_serie(self):
        """Set data_serie to an empty pandas serie."""
        self.data_serie = []

    def add_meta_variables(self):
        """Add meta variables to self.data_serie."""
        row = '{}=\"{}\"'
        for para in self.meta_spec['columns']:
            self.selected_columns.add(para)
            self.data_serie.append(
                ''.join(
                    (
                        self.meta_block_prefix,
                        self.meta_spec.get('prefix'),
                        self.meta_spec['seperator'].join(
                            (row.format(k, v)
                             for k, v in self.pmap[para].items())
                        ),
                        self.meta_spec.get('suffix')
                    )
                )
            )
        self.data_serie.append(self.meta_block_prefix)

    def add_data_variables(self, df):
        """Add data variables to self.data_serie."""
        row = '{}=\"{}\"'
        for para in df.data_columns:
            if para not in self.ices_mapping_spec \
                    or para in self.meta_spec['columns']:
                continue
            self.selected_columns.add(para)
            self.data_serie.append(
                ''.join(
                    (
                        self.meta_block_prefix,
                        self.data_spec.get('prefix'),
                        self.data_spec['seperator'].join(
                            (row.format(k, v)
                             for k, v in self.pmap[para].items())
                        ),
                        self.data_spec.get('suffix')
                    )
                )
            )
        self.data_serie.append(self.meta_block_prefix)

    def add_ices_mapping(self, df):
        """Add ICES parameter mapping to self.data_serie."""
        row = '<subject>ICES:{}:{}</subject>' \
              '<object>ICES:{}::{}</object>' \
              '<units>ICES:{}::{}</units>'
        self.data_serie.append(
            self.meta_block_prefix + 'ICES_parameter_mapping'
        )
        for para in df.data_columns:
            if para not in self.ices_mapping_spec:
                continue
            para_args = []
            for k, v in self.ices_mapping_spec[para].items():
                para_args.append(k)
                para_args.append(v)
            self.data_serie.append(
                ''.join(
                    (
                        self.meta_block_prefix,
                        row.format(*para_args)
                    )
                )
            )
        self.data_serie.append(self.meta_block_prefix)

    def add_data_table(self, df):
        """Add data table to self.data_serie."""
        mapper = {c: self.pmap[c]['label']
                  for c in df.columns if c in self.pmap}

        col_order = self.meta_spec['columns'].copy()
        col_order.extend(
            [c for c in df.columns if c not in col_order and self._in_map(c)]
        )
        self._empty_redundant_meta_columns(df)
        df = df[col_order].rename(columns=mapper)

        self.data_serie.append('\t'.join(df.columns))
        self.data_serie.extend(
            df.apply(lambda x: '\t'.join(x), axis=1).to_list()
        )

    def _empty_redundant_meta_columns(self, df):
        """Set '' on redundant meta rows.

        Keep meta information only on the first row.
        Example:
            Original:
                'Cruise'	'Station'	'Reported station name'	'Type'
                '202177SE01'	'2021_77SE_0001'	'SLÄGGÖ'	'B'...
                '202177SE01'	'2021_77SE_0001'	'SLÄGGÖ'	'B'...
                '202177SE01'	'2021_77SE_0002'	'Å13'	'B'...
                '202177SE01'	'2021_77SE_0002'	'Å13'	'B'...
            will become:
                'Cruise'	'Station'	'Reported station name'	'Type'
                '202177SE01'	'2021_77SE_0001'	'SLÄGGÖ'	'B'...
                ''	''	''	''...
                '202177SE01'	'2021_77SE_0002'	'Å13'	'B'...
                ''	''	''	''...
        """
        meta_columns = self.meta_spec['columns'].copy()
        for c in meta_columns:
            qf = 'Q_' + c
            if qf in df:
                meta_columns.append(qf)
        df.loc[df[['KEY', 'SMTYP']].duplicated(keep='first'), meta_columns] = ''

    def _in_map(self, name):
        """Return bool.

        Check if name exists in writer mapping attributes.
        """
        if name.startswith('Q_'):
            if name[2:] in self.ices_mapping_spec:
                return True
            else:
                return False
        elif name not in self.selected_columns:
            return False
        elif name in self.pmap:
            return True
        elif name in self.ices_mapping_spec:
            return True
        else:
            return False

    @staticmethod
    def divide_on_smtyp(df):
        """Divide dataframe based on sampling type (SMTYP)."""
        df_cdf = None
        ctd_cols = [c for c in df.columns if '_CTD' in c]
        if ctd_cols:
            frame_cols = df.meta_columns + ctd_cols
            df_cdf = df.loc[:, frame_cols].copy()
            df_cdf.rename(
                columns={c: c.replace('_CTD', '') for c in ctd_cols},
                inplace=True
            )
            df.drop(columns=ctd_cols, inplace=True)
            df_cdf['SMTYP'] = 'C'
            df_cdf['SMCAT'] = '130'

        df.rename(
            columns={c: c.replace('_BTL', '') for c in df.columns},
            inplace=True
        )
        df['SMTYP'] = 'B'
        df['SMCAT'] = '30'
        if ctd_cols:
            for c in ctd_cols:
                valid_col = c.replace('_CTD', '')
                if valid_col not in df:
                    df[valid_col] = ''
            df = df.append(df_cdf, ignore_index=True)
        return df
