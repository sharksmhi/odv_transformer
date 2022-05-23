#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-21 21:18

@author: johannes
"""
from odv_transformer import Session


if __name__ == "__main__":
    s = Session()
    arch_name = 'SHARK_Chlorophyll_2020_SMHI_version_2022-01-11.zip'
    s.read(
        s.settings.base_directory.joinpath('tests', 'test_data', arch_name),
        reader='chl_tube',
        delivery_name='SHARK_Chlorophyll_2020_SMHI',
    )
    s.write(
        writer='ices',
        delivery_name='SHARK_Chlorophyll_2020_SMHI',
        file_name=arch_name.split('.')[0].lower(),
    )
