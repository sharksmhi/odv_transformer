#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
from odv_transformer.handler import get_key
from odv_transformer.writers.writer import WriterBase, write_with_numpy
import re


def adjust_cruise_no(cruise, old, shipc):
    """If shipc should be mapped we map cruise_no as well."""
    return cruise.replace(old, shipc)
    # return ''.join((cruise[:4], shipc, cruise[8:]))


def set_depth_column_positions(col_order):
    """Place DEPH, MNDEP and MXDEP together in dataframe."""
    if 'DEPH' in col_order and 'MNDEP' in col_order:
        di = col_order.index('DEPH') + 1
        data_params = [c for c in col_order[di:] if c not in {'MNDEP', 'MXDEP'}]
        return col_order[:di] + ['MNDEP', 'MXDEP'] + data_params
    else:
        return col_order


class IcesOdvWriter(WriterBase):
    """Convert NODC format into ICES ODV delivery format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.encoding = 'utf-8'
        self.meta_block_prefix = None
        self.meta_spec = None
        self.data_spec = None
        self.parameters = None
        self.pmap = None
        self.smap = {
            '7774': 'ZZ99',
            # '7791': 'ZZ99',
            '7798': 'ZZ99',
            '77Svävare': '77NA'
        }
        self.selected_columns = set()
        self.special_mapping = None
        super().__init__(*args, **kwargs)
        if self.parameters:
            self.parameters = set(self.parameters)

    def write(self, file_path, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        self._set_parameter_mapping(pmap)
        self._reset_serie()
        self._map_shipc(data['data'])

        df = self.clean_cruise_no(data['data'], keep_cruise_no=False)
        df = self.divide_on_smtyp(data['data'], keep_ctd_data=False)
        # test of a different method
        # df = self.add_sampling_type(data['data'])
        df.delete_rows_with_no_data()

        self.add_encoding_information()
        self.add_meta_variables(df)
        self.add_data_variables(df)
        self.add_ices_mapping(df)
        self.add_data_table(df)

        self._write(file_path)

    def _write(self, fid):
        """Write data to file according to ICES ODV format."""
        print(f'writing to: {fid}')
        write_with_numpy(fid, self.data_serie, fmt='%s', encoding=self.encoding)

    def _reset_serie(self):
        """Set data_serie to an empty pandas serie."""
        self.data_serie = []

    def _set_parameter_mapping(self, pmap):
        """Initialize the parameter mapping.

        Look for special mapping according to writer.
        """
        if self.special_mapping:
            for key, item in self.special_mapping.items():
                pmap[key] = item  # Overwrite if exists.
        self.pmap = pmap

    def add_encoding_information(self):
        """Add file information to self.data_serie"""
        self.data_serie.append(f"//<Encoding>{self.encoding.upper()}</Encoding>")

    def add_meta_variables(self, df):
        """Add meta variables to self.data_serie."""
        row = '{}=\"{}\"'
        for para in self.meta_spec['columns']:
            if para not in df:
                continue
            self.selected_columns.add(para)
            self.data_serie.append(
                ''.join(
                    (
                        self.meta_block_prefix,
                        self.meta_spec.get('prefix'),
                        self.meta_spec['seperator'].join(
                            (row.format(k, self.pmap[para].get(k))
                             for k in self.meta_spec.get('field_list'))
                        ),
                        self.meta_spec.get('suffix')
                    )
                )
            )
        self.data_serie.append(self.meta_block_prefix)

    def validate_parameter_name(self, parameter, data_columns):
        """Validate the given parameter and return name if ok."""
        _p = parameter.split()[0]
        if _p not in data_columns:
            return None
        if parameter not in self.pmap:
            if _p not in self.pmap:
                return None
            parameter = _p
        if (parameter not in self.parameters and _p not in self.parameters) or (
                parameter in self.meta_spec['columns']):
            return None
        return parameter

    def add_data_variables(self, df):
        """Add data variables to self.data_serie."""
        row = '{}=\"{}\"'
        for para in df.columns:
            para = self.validate_parameter_name(para, df.data_columns)
            if not para:
                continue
            self.selected_columns.add(para)
            self.data_serie.append(
                ''.join(
                    (
                        self.meta_block_prefix,
                        self.data_spec.get('prefix'),
                        self.data_spec['seperator'].join(
                            (row.format(k, self.pmap[para].get(k))
                             for k in self.data_spec.get('field_list'))
                        ),
                        self.data_spec.get('suffix')
                    )
                )
            )
        self.data_serie.append(self.meta_block_prefix)

    def get_ices_mapper(self, parameter):
        """Return mapper.

        Validate and return a mapping object associated to the given parameter.
        """
        _p = parameter.split()[0]
        if _p not in self.parameters:
            return None
        if parameter in self.pmap:
            mapper = self.pmap.get(parameter)
        else:
            mapper = self.pmap.get(_p)
        return mapper

    def add_ices_mapping(self, df):
        """Add ICES parameter mapping to self.data_serie."""
        row = '<subject>ICES:LOCAL:{LOCAL}</subject>' \
              '<object>ICES:P01::{P01}</object>' \
              '<units>ICES:P06::{P06}</units>'
        self.data_serie.append(
            self.meta_block_prefix + 'ICES_parameter_mapping')
        for para in df.data_columns:
            mapper = self.get_ices_mapper(para)
            if not mapper:
                continue
            self.data_serie.append(
                self.meta_block_prefix + row.format_map(mapper))
        self.data_serie.append(self.meta_block_prefix)

    def get_data_mapper(self, columns):
        """Return mapper.

        Validate and return a mapping object associated to the given columns.
        """
        mapper = {}
        for c in columns:
            if c in self.pmap:
                val = self.pmap[c].get('label')
            else:
                _c = c.split()[0]
                if _c not in self.pmap:
                    continue
                val = self.pmap[_c].get('label')
            mapper.setdefault(c, val)
        return mapper

    def add_data_table(self, df):
        """Add data table to self.data_serie."""
        mapper = self.get_data_mapper(df.columns)

        col_order = [c for c in self.meta_spec['columns'] if c in df]
        col_order.extend(
            [c for c in df.columns if c not in col_order and self._in_map(c)])
        col_order = set_depth_column_positions(col_order)

        self._empty_redundant_meta_columns(df)
        df = df[col_order].rename(columns=mapper)

        self.data_serie.append('\t'.join(df.columns))
        self.data_serie.extend(
            df.apply(lambda x: '\t'.join(x), axis=1).to_list())

    def _map_shipc(self, df):
        """Map ship to ICES VOCAB."""
        # Don´t use late binding closures.
        # https://docs.python-guide.org/writing/gotchas/#late-binding-closures
        ship_set = set(df['SHIPC'])
        for shipc, ices_code in self.smap.items():
            if shipc in ship_set:
                boolean = df['SHIPC'] == shipc
                df.loc[boolean, 'SHIPC'] = ices_code
                df['KEY'] = df[['MYEAR', 'SHIPC', 'SERNO']].apply(
                    get_key, axis=1
                )
                df.loc[boolean, 'CRUISE_NO'] = [
                    adjust_cruise_no(x, shipc, ices_code)
                    for x in df.loc[boolean, 'CRUISE_NO']
                ]
                # df.loc[boolean, 'CRUISE_NO'] = df.loc[boolean,
                #                                       'CRUISE_NO'].apply(
                #     lambda x: adjust_cruise_no(x, shipc, ices_code)
                # )

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
                # relevant for SECCHI (which counts as visit metadata)
                meta_columns.append(qf)

        df.sort_values(by=['SMTYP', 'KEY'], inplace=True)
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

    @staticmethod
    def clean_cruise_no(df, keep_cruise_no=True):
        print('Cleaning CRUISE_NO')
        df['CRUISE_NO'] = df['CRUISE_NO'].str.lstrip('0')
        return df

    @staticmethod
    def drop_ctd_cols(df):
        """
            Drop CTD_column
        """
        pass


    @staticmethod
    def divide_on_smtyp(df, keep_ctd_data = True):
        """
            Divide dataframe based on sampling type (SMTYP) and set Device category codes
            Device category codes according to L05 (SEADATANET DEVICE CATEGORIES)
            https://vocab.seadatanet.org/v_bodc_vocab_v2/search.asp?lib=L05
        """
        print('Dividing on sampling type')
        df_cdf = None
        ctd_cols = [c for c in df.columns if '_CTD' in c]

        # CTD data has device category code 130 and sample type C
        # To include low res CTD data as if it was bottle data ICES suggests to use Device code 30 for this too.
        if ctd_cols:
            frame_cols = df.meta_columns + ctd_cols
            btl_cols = [c for c in df.columns if c not in frame_cols]
            df_cdf = df.copy()
            df_cdf[btl_cols] = ''
            df_cdf['SMTYP'] = 'C'
            df_cdf['SMCAT'] = '130'

            df[ctd_cols] = ''

        # Bottle data has device category code 30 and sample type B
        if 'DEPH' in df and 'MNDEP' not in df:
            df['SMTYP'] = 'B'
            df['SMCAT'] = '30'
        # Hose samples, set same code as bottle 
        elif 'MNDEP' in df:
            # TODO tube samples should have different codes.
            df['SMTYP'] = 'B'  # Can´t find a code for tube/hose sampling
            df['SMCAT'] = '30'  # Can´t find a code for tube/hose sampling

        if ctd_cols and keep_ctd_data:
            df = df.append(df_cdf, ignore_index=True)

        return df
    @staticmethod
    def add_sampling_type(df, type = 'B', category = '30'):
        df['SMTYP'] = type
        df['SMCAT'] = category

        return df


class IcesProfileOdvWriter(IcesOdvWriter):
    """Convert NODC Profile format into ICES ODV delivery format.

    Intended for high resolution profile data such as CTD / MVP / STD.
    """

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)

    def write(self, file_path, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        self._set_parameter_mapping(pmap)
        self._reset_serie()
        self._map_shipc(data['data'])
        self._set_smtyp(data['data'])

        self.add_meta_variables(data['data'])
        self.add_data_variables(data['data'])
        self.add_ices_mapping(data['data'])
        self.add_data_table(data['data'])
        self._write(file_path)

    def _in_map(self, name):
        """Return bool.

        Check if name exists in writer mapping attributes.
        """
        if name.startswith('Q_'):
            if name[2:] in self.parameters:
                return True
            else:
                return False
        elif name in self.parameters or name.split()[0] in self.parameters:
            return True
        else:
            return False

    @staticmethod
    def _set_smtyp(df):
        """Set sampling type (SMTYP) to data."""
        df['SMTYP'] = 'C'
        df['SMCAT'] = '130'
