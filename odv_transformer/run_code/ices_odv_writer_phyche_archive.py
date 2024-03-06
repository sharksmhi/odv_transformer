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
    arch_name = r'SHARK_PhysicalChemical_2022_IBT_SMHI_version_2023-12-22.zip'  # phyche_archive
    #arch_name = r'SHARK_PhysicalChemical_2022_BAS_SMHI_version_2023-12-15.zip'
    delivery_name = arch_name.split(".")[0]
    
    s.read(
        Path(r'\\winfs\data\prodkap\sharkweb\SHARKdata_datasets').joinpath(arch_name),
        reader='phyche_archive',
        delivery_name=delivery_name
    )
    s.write(
        writer='ices',
        delivery_name=delivery_name,
        file_name=arch_name.split('.')[0].lower(),
    )
