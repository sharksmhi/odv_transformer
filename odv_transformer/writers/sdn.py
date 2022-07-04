#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 18:22

@author: johannes
"""
from odv_transformer.utils import get_time_now
from odv_transformer.writers.writer import WriterBase, write_with_numpy
from odv_transformer.writers.cdi import CdiWriter
from odv_transformer.readers.sharklog import LogReader


CDI_META_COLUMNS = [
    'SERNO', 'SDATE', 'STIME', 'WADEP', 'LATIT_DD', 'LONGI_DD', 'SHIPC',
    'STATN_NOM', 'STATN', 'ORDERER', 'SEQNO', 'LOCAL_CDI_ID', 'REV_DATE', 'P02'
]


def add_cdi_id(seqno):
    """Insert CDI-id."""
    return f'seqno_{seqno}_H09'


def adjust_cruise_no(cruise):
    """If shipc should be mapped we map cruise_no as well."""
    if len(cruise) > 7:
        return '_'.join((cruise[:4], cruise[4:8], cruise[8:]))
    else:
        return cruise


class LogHandler:
    """Handler of the SHARK-log (Physical and Chemical data archive).

    Primarily use case: Return the CDI-id associated to a given sequence number.
    """

    def __init__(self):
        """Initialize."""
        self._df = None
        self.log = LogReader(table='sharkintlog')

    def get_info(self, seqno, key=None):
        """Return value based on the given arguments.

        Args:
            seqno (int or list): Main purpose is to give an integer as input.
                                 However, it is possible to use a list of
                                 seqnos as well.
            key (str):
        """
        if key:
            return self.df.loc[seqno, key]
        else:
            return None

    @property
    def df(self):
        """Return dataframe."""
        return self._df

    @df.setter
    def df(self, seqno_list):
        """Set internal dataframe.

        Using seqno (integers) as index.

        Args:
            seqno_list (list): list of sequence numbers.
        """
        _df = self.log.get_data_for_seqno_list(seqno_list)
        self._df = _df.set_index('seqno')


SHARK_LOG = LogHandler()


def get_cdi_id(seqno):
    """Return CDI-id.

    If the given seqno is associated to a CDI-id that id will be returned.
    Otherwise, a new one will be created according to the function add_cdi_id.

    Args:
        seqno (int/str): Sequence number
    """
    cdi = SHARK_LOG.get_info(int(seqno), key='cdi_id')
    if cdi:
        return cdi
    else:
        return add_cdi_id(seqno)


def get_nominal_name(seqno):
    """Return nominal station name.

    Args:
        seqno (int/str): Sequence number
    """
    name = SHARK_LOG.get_info(int(seqno), key='statn')
    return name


class SdnOdvWriter(WriterBase):
    """Convert NODC format into SeaDataNet ODV delivery format."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.meta_block_prefix = None
        self.meta_spec = None
        self.data_spec = None
        self.cdi_data = {}
        self.parameters = set()
        self.pmap = None
        self.selected_columns = set()
        self.selected_data_columns = set()
        self.special_label_mapping = None
        self.meta = {'encoding': 'cp1252'}
        super().__init__(*args, **kwargs)
        if self.data_spec:
            self.parameters = set(self.data_spec['columns'])

    def _update_meta(self, df):
        """Change attributes of meta dictionary."""
        self.meta['revdate'] = get_time_now()
        self.meta['Ship'] = df.iloc[0]['SHIPC']
        self.meta['Seqno'] = df.iloc[0]['SEQNO']

    def _update_selected_columns(self, df):
        """Check which columns exists and add them to self.selected_columns."""
        for p in self.meta_spec['columns']:
            if p in df.columns:
                if df[p].any():
                    self.selected_columns.add(p)
        for p in self.data_spec['columns']:
            if p in df.columns:
                if df[p].any():
                    self.selected_columns.add(p)
                    self.selected_data_columns.add(p)

    def get_p02_codes(self, df):
        """Extract P02 codes from data."""
        data_exists = df.any()
        p02_codes = set()
        for p in self.selected_data_columns:
            if data_exists[p] and p in self.pmap:
                code = self.pmap[p].get('P02')
                if code:
                    p02_codes.add(code)
        return sorted(p02_codes)

    def _update_cdi_data(self, df):
        """Add new data to the CDI record."""
        seqno = self.meta.get('Seqno')
        self.cdi_data.setdefault(seqno, {})
        self.cdi_data[seqno]['SEQNO'] = seqno
        self.cdi_data[seqno]['REV_DATE'] = self.meta.get('revdate')
        self.cdi_data[seqno]['P02'] = self.get_p02_codes(df)
        for key in CDI_META_COLUMNS:
            if key in self.cdi_data[seqno]:
                continue
            self.cdi_data[seqno][key] = df.iloc[0][key]

    def _add_data(self, df):
        """Set sampling type to data.

        For this writer sampling type will always be "B" for bottle sampling.
        """
        df['SMTYP'] = 'B'
        df['Q_DEPH'] = ''
        df['LOCAL_CDI_ID'] = df['SEQNO'].apply(get_cdi_id)
        df['STATN_NOM'] = df['SEQNO'].apply(get_nominal_name)
        df['CRUISE_NO'] = df['CRUISE_NO'].apply(adjust_cruise_no)
        self._map_quality_flags(df)
        df.delete_rows_with_no_data()

    def _map_quality_flags(self, df):
        """Change quality flags according to SeaDataNet standard."""
        for qf in df.quality_flag_columns:
            boolean = df[qf[2:]].ne('') | df[qf].eq('M')
            df.loc[boolean, qf] = df.loc[boolean, qf].replace(
                self.data_spec['flag_mapping']
            )
            boolean = df[qf[2:]].eq('')
            df.loc[boolean, qf] = '9'

    def write(self, file_structure, data, pmap=None, **kwargs):
        """Write data to ODV txt format."""
        SHARK_LOG.df = map(int, data['data']['SEQNO'].unique())
        self._set_parameter_mapping(pmap)
        self._add_data(data['data'])

        for key in data['data']['KEY'].unique():
            self._reset_serie()
            df = data['data'].loc[data['data']['KEY'] == key, :]
            self._update_meta(df)
            self._update_selected_columns(df)
            self._update_cdi_data(df)

            self.add_metadata()
            self.add_sdn_mapping(df)
            self.add_data_table(df)

            self._write(
                str(file_structure).format_map({
                    'SEQNO': self.meta.get('Seqno')})
            )

        self._write_cdi_record(file_structure.parent, **kwargs)

    def _write(self, fid):
        """Write data to file according to ICES ODV format."""
        print(f'writing to: {fid}')
        write_with_numpy(fid, self.data_serie, fmt='%s', encoding='cp1252')

    def _write_cdi_record(self, path, **kwargs):
        """Write CDI record to JSON file."""
        cdi = CdiWriter(**kwargs)
        cdi.add_data(self.cdi_data)
        cdi.write(path)

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
        self.data_serie.append(self.meta_block_prefix + 'SDN_parameter_mapping')
        for para in df.data_columns:
            _p = para.split()[0]
            if _p not in self.parameters or _p not in self.selected_columns:
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
        for c in self.data_spec['columns']:
            if c in col_order:
                continue
            if self._in_map(c):
                col_order.append(c)
                col_order.append('Q_' + c)
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
