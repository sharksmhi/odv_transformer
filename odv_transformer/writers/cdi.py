#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-14 14:23

@author: johannes
"""
import pandas as pd


class CdiWriter:
    """Writer for CDI basis according to MIKADO format."""

    header = [
        'serie', 'year', 'date', 'depth', 'longitude', 'latitude', 'kod',
        'ship', 'ship_type', 'station', 'alt_stn_name', 'originator', 'seqno',
        'revdate', 'mindepth', 'maxdepth', 'local_cdi_id'
    ]

    mapper = {
        'serie': 'SERNO',
        'depth': 'WADEP',
        'latitude': 'LATIT_DD',
        'longitude': 'LONGI_DD',
        'ship': 'SHIPC',
        'station': 'STATN_NOM',
        'alt_stn_name': 'STATN',
        'originator': 'ORDERER',
        'seqno': 'SEQNO',
        'local_cdi_id': 'LOCAL_CDI_ID',
        'revdate': 'REV_DATE',
        'kod': 'P02'
    }

    def __init__(self, lmap=None, smap=None, **kwargs):
        """Initialize.

        Args:
            lmap (dictionary): mapping of LABO codes
            smap (dictionary): mapping of ship codes
        """
        self.lmap = lmap
        self.smap = smap
        self.df = pd.DataFrame()

    def get_labos(self, orderers):
        """Map LABO codes and return list."""
        labos = []
        for labo in orderers.split(','):
            mapped_labo = self.lmap.get(labo.strip())
            if mapped_labo:
                labos.append(mapped_labo)
        return labos

    def add_data(self, data):
        """Add data according to MIKADO format.

        Args:
            data (dict): Dictionary with seqno(s) as key(s).
        """
        def get_array(value):
            return [value] * length * labo_length

        def get_labo_array(value):
            new_list = [value[0]] * length
            for labo in value[1:]:
                new_list.extend([labo] * length)
            return new_list

        for item in data.values():
            labos = self.get_labos(item['ORDERER'])
            if not labos:
                continue
            length = len(item['P02'])
            labo_length = len(labos)

            tmp = {}
            for key in self.header:
                if key == 'year':
                    tmp[key] = get_array(item['SDATE'][:4])
                elif key == 'date':
                    if item.get('STIME'):
                        tmp[key] = get_array('T'.join(
                            (item.get('SDATE')[4:], item.get('STIME')))
                        )
                    else:
                        tmp[key] = get_array(item.get('SDATE'))
                elif key == 'kod':
                    tmp[key] = item.get('P02') * labo_length
                elif key == 'originator':
                    tmp[key] = get_labo_array(labos)
                elif key == 'ship_type':
                    tmp[key] = get_array(self.smap.get(item.get('SHIPC'), ''))
                else:
                    tmp[key] = get_array(item.get(self.mapper.get(key), ''))
            self.df = self.df.append(pd.DataFrame(tmp), ignore_index=True)

    def write(self, directory):
        """Write dataframe to text file."""
        self.df.to_csv(
            directory.joinpath('mikado_bottle.txt'),
            sep='\t',
            index=False,
            encoding='cp1252'
        )
