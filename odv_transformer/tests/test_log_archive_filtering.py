#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-07-04 10:10

@author: johannes
"""
from pathlib import Path
from odv_transformer import Session
from frigate import FilterOptions, get_data


ARCHIVE_PATH = Path(r'C:\Arbetsmapp\datasets\PhysicalChemical')
MAPPING = {
    'year': 'MYEAR',
    'ship': 'SHIPC',
    'serno': 'SERNO',
    'seqno': 'SEQNO',
    'proj': 'PROJ',
    'orderer': 'ORDERER'
}


if __name__ == "__main__":
    filter_opt = FilterOptions(
        year=['2020'],
        ship=['77SE'],
    )
    archives = get_data(
        db_path=str(ARCHIVE_PATH.joinpath('sharklog.db')),
        template_name='tmp_archives.jinja',
        filter_obj=filter_opt,
        template_kwargs=dict(
            table='sharkintlog',
            select_statement='distinct',
            field='year, archive_name'
        )
    )

    s = Session()

    for row in archives.itertuples():
        print(row.archive_name)
        s.read(
            str(ARCHIVE_PATH.joinpath(row.year, row.archive_name)),
            reader='phyche_archive',
            delivery_name=row.archive_name,
            filters={
                MAPPING.get(key): item
                for key, item in filter_opt.in_list_filter.items()
            }
        )

    s.merge(
        deliveries=list(s.deliveries),
        new_name='merged'
    )
