#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-10 15:23

@author: johannes
"""
from odv_transformer import Session


if __name__ == "__main__":
    s = Session()

    s.read(
        s.settings.base_directory.joinpath(
            'tests', 'test_data', 'SHARK_PhysicalChemical_2021_BAS_SMHI'
        ),
        reader='phyche_archive',
        delivery_name='SHARK_PhysicalChemical_2021_BAS_SMHI',
    )

    s.read(
        s.settings.base_directory.joinpath(
            'tests', 'test_data',
            'SHARK_Chlorophyll_2021_SMHI_version_2022-05-02.zip'
        ),
        reader='chl_tube',
        delivery_name='SHARK_Chlorophyll_2021_SMHI',
    )

    s.merge(
        deliveries=['SHARK_PhysicalChemical_2021_BAS_SMHI',
                    'SHARK_Chlorophyll_2021_SMHI'],
        new_name='merged'
    )

    s.write(
        writer='ices',
        delivery_name='merged',
        file_name='SHARK_PhysicalChemical_Chlorophyll_2021_BAS_SMHI'.lower(),
    )
