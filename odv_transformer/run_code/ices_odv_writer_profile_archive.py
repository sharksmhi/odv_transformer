#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 13:40

@author: johannes
"""
from pathlib import Path
from odv_transformer import Session

if __name__ == "__main__":
    s = Session()
    folder = '//winfs-proj/data/proj/sharknet/ctd_backup/Leveranser_DV/2023'
    delivery_name = 'dv_delivery_2022-08-21_2022-09-01' #IBTS Q3 2022
    delivery_name = 'dv_delivery_2023-01-25_2023-02-07' #IBTS Q1 2023

    folder = r'\\winfs-proj\proj\havgem\LenaV\temp'
    delivery_name = 'odv_transform_tests'

    archive_path = Path(
        f'{folder}/{delivery_name}')
    if not archive_path.exists():
        raise FileExistsError(f'incorrect path {archive_path}')
    s.read(
        str(archive_path),
        reader='profile',
        delivery_name=archive_path.name,
    )

    s.write(
        writer='ices_profile',
        delivery_name=archive_path.name,
        file_name=archive_path.name.lower(),
    )
