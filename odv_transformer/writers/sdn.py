#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
from odv_transformer.writers.writer import WriterBase, write_with_numpy


def adjust_cruise_no(cruise, shipc):
    """If shipc should be mapped we map cruise_no as well."""
    return ''.join((cruise[:4], shipc, cruise[8:]))


class SdnOdvWriter(WriterBase):
    """Convert NODC format into SeaDataNet ODV delivery format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.meta_block_prefix = None
        self.meta_spec = None
        self.data_spec = None
        self.parameters = set()
        self.pmap = None
        self.selected_columns = set()
        self.special_label_mapping = None
        self.meta = {'encoding': 'cp1252'}
        super().__init__(*args, **kwargs)
        if self.data_spec:
            self.parameters = set(self.data_spec['columns'])

    def _update_meta(self, df):
        """Change attributes of meta dictionary."""
        self.meta['Ship'] = df.iloc[0]['SHIPC']
        self.meta['Seqno'] = df.iloc[0]['SEQNO']

    def _update_selected_columns(self, df):
        """Check which columns exists and add them to self.selected_columns."""
        for p in self.meta_spec['columns'] + self.data_spec['columns']:
            if p in df.columns:
                self.selected_columns.add(p)

    @staticmethod
    def _set_smtyp(df):
        """Set sampling type to data.

        For this writer sampling type will always be "B" for bottle sampling.
        """
        df['SMTYP'] = 'B'

    def _map_quality_flags(self, df):
        """Change quality flags according to SeaDataNet standard."""
        for qf in df.quality_flag_columns:
            boolean = df[qf[2:]].ne('') | df[qf].eq('M')
            df.loc[boolean, qf] = df.loc[boolean, qf].replace(
                self.data_spec['flag_mapping']
            )

    def write(self, file_path, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        self._set_parameter_mapping(pmap)
        self._set_smtyp(data['data'])
        self._map_quality_flags(data['data'])

        for key in data['data']['KEY'].unique():
            self._reset_serie()
            df = data['data'].loc[data['data']['KEY'] == key, :]
            df.delete_rows_with_no_data()
            self._update_meta(df)
            self._update_selected_columns(df)

            self.add_metadata()
            self.add_sdn_mapping(df)
            self.add_data_table(df)

            self._write(str(file_path).format_map(
                {'SEQNO': self.meta.get('Seqno')}
            ))

    def _write(self, fid):
        """Write data to file according to ICES ODV format."""
        print(f'writing to: {fid}')
        write_with_numpy(data=self.data_serie, save_path=fid)

    def _reset_serie(self):
        """Set data_serie to an empty pandas serie."""
        self.data_serie = []
        self.selected_columns = set()

    def _set_parameter_mapping(self, pmap):
        """Initialize the parameter mapping.

        Look for special mapping according to writer.
        """
        if self.special_label_mapping:
            for key, item in self.special_label_mapping.items():
                pmap[key] = item  # Overwrite if exists.
        self.pmap = pmap

    def add_metadata(self):
        """Add meta blocks to self.data_serie."""
        row = '{}: {}'
        for k, v in self.meta.items():
            self.data_serie.append(
                ''.join((self.meta_block_prefix, row.format(k, v)))
            )
        self.data_serie.append(self.meta_block_prefix)

    def add_sdn_mapping(self, df):
        """Add SeaDataNet parameter mapping to self.data_serie."""
        row = '<subject>SDN:LOCAL:{LOCAL}</subject>' \
              '<object>SDN:P01::{P01}</object>' \
              '<units>SDN:P06::{P06}</units>'
        self.data_serie.append(self.meta_block_prefix +
                               'SDN_parameter_mapping')
        for para in df.data_columns:
            _p = para.split()[0]
            if _p not in self.parameters:
                continue
            if para in self.pmap:
                mapper = self.pmap.get(para)
            else:
                mapper = self.pmap.get(_p)
            self.data_serie.append(
                self.meta_block_prefix + row.format_map(mapper))
        self.data_serie.append(self.meta_block_prefix)

    def add_data_table(self, df):
        """Add data table to self.data_serie."""
        col_order = [c for c in self.meta_spec['columns'] if c in df]
        col_order.extend(
            [c for c in df.columns if c not in col_order and self._in_map(c)])
        self._empty_redundant_meta_columns(df)
        df = df[col_order]

        header = self.get_header(df.columns)
        self.data_serie.append('\t'.join(header))
        self.data_serie.extend(
            df.apply(lambda x: '\t'.join(x), axis=1).to_list())

    def get_header(self, columns):
        """Map header according to SDN format."""
        new = []
        for col in columns:
            if col.startswith('Q_'):
                # SDN are using the same column name for all parameters.
                new.append('QV:SEADATANET')
            elif col in self.pmap:
                new.append(self.pmap[col].get('label'))
            else:
                _c = col.split()[0]
                if _c not in self.pmap:
                    raise ValueError(f'{col} and/or {_c} are not in parameter '
                                     f'mapping, nor in special mapping')
                new.append(self.pmap[_c].get('label'))
        return new

    def _empty_redundant_meta_columns(self, df):
        """Set '' on redundant meta rows.

        Keep meta information only on the first row.
        Example:
            Original:
                'Cruise'	'Station'	'Type'
                '2021_77SE_01'	'SLÄGGÖ'	'B'...
                '2021_77SE_01'	'SLÄGGÖ'	'B'...
            will become:
                'Cruise'	'Station'	'Type'
                '2021_77SE_01'	'SLÄGGÖ'	'B'...
                ''	''	''...
        """
        meta_columns = self.meta_spec['columns'].copy()
        for c in meta_columns:
            qf = 'Q_' + c
            if qf in df:
                # relevant for SECCHI (which counts as visit metadata)
                meta_columns.append(qf)
        df.loc[df[['KEY', 'SMTYP']].duplicated(keep='first'), meta_columns] = ''

    def _in_map(self, name):
        """Return bool.

        Check if name exists in writer mapping attributes.
        """
        if name.startswith('Q_'):
            if name[2:] in self.parameters:
                return True
            else:
                return False
        elif name not in self.selected_columns:
            return False
        elif name in self.pmap:
            return True
        elif name in self.parameters:
            return True
        else:
            return False
