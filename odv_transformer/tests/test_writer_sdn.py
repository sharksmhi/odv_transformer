#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 13:40

@author: johannes
"""
from odv_transformer import Session


if __name__ == "__main__":
    s = Session()
    arch_name = 'SHARK_PhysicalChemical_2021_BAS_SMHI'
    s.read(
        s.settings.base_directory.joinpath('tests', 'test_data', arch_name),
        reader='phyche_archive',
        delivery_name=arch_name,
    )
    s.write(
        writer='sdn',
        delivery_name=arch_name,
        file_name=arch_name.lower(),
    )
