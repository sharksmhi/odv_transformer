#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2023-02-03 13:40

@author: Lena modified from original by johannes
"""
from pathlib import Path
from odv_transformer import Session


if __name__ == "__main__":
    s = Session()
    archives = [
                {'name': 'SHARK_PhysicalChemical_2023_EXT_SMHI_version_2024-09-28.zip', 'reader': 'phyche_archive'},
                {'name': 'SHARK_PhysicalChemical_2023_BAS_SMHI_version_2024-09-30.zip', 'reader': 'phyche_archive'},
                {'name': 'SHARK_PhysicalChemical_2023_IBT_SMHI_version_2024-09-28.zip', 'reader': 'phyche_archive'},
                {'name': 'SHARK_PhysicalChemical_2023_EKO_SMHI_version_2024-09-28.zip', 'reader': 'phyche_archive'},
                ]

    # Cannot read Physical/Cemical  from zip-filepackage, needs to be unpacked.
    deliveries = []
    new_filename = '_'.join(archives[0]["name"].split(".")[0].split('_')[:3])
    for archive in archives:
        delivery_name = archive["name"].split(".")[0]
        new_filename += '_'+'_'.join(delivery_name.split('_')[3:])
        s.read(
        # Path(r'\\winfs\data\prodkap\sharkweb\SHARKdata_datasets').joinpath(archive["name"]),
        Path(r'C:\Users\a002573\Desktop\smhi fyskem 2023').joinpath(archive["name"]),
        reader=f'{archive["reader"]}',
        delivery_name=f'{delivery_name}',
        )
        deliveries.append(delivery_name)


    s.merge(
        deliveries=deliveries,
        new_name='merged'
    )

    s.write(
        writer='ices',
        delivery_name='merged',
        file_name=new_filename.lower().replace('version', 'vs'),
    )
