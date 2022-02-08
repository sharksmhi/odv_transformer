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
        super().__init__(*args, **kwargs)

    def write(self, file_path, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        self.pmap = pmap
        self._reset_serie()

        self.add_meta_variables()
        self.add_data_variables(data['data'])
        self.add_ices_mapping(data['data'])
        self.add_data_table(data['data'])

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
        for para in self.meta_spec['mandatory']:
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
            if para not in self.ices_mapping_spec:
                continue
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

        col_order = self.meta_spec['mandatory'].copy()
        col_order.extend(
            [
                c for c in df.columns if
                c not in col_order and c in self.pmap and
                c in self.ices_mapping_spec
            ]
        )
        df = df[col_order].rename(columns=mapper)

        self.data_serie.append('\t'.join(df.columns))
        self.data_serie.extend(
            df.apply(lambda x: '\t'.join(x), axis=1).to_list()
        )
