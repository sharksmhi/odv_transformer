#!/usr/bin/env python3
"""
Created on 2022-02-03 11:03

@author: johannes
"""
from odv_transformer import Session


if __name__ == "__main__":
    s = Session()

    arch = r'C:\PhysicalChemical\2021\SHARK_PhysicalChemical_2021_EXT_SMHI'
    s.read(
        arch,
        reader='phyche_archive',
        delivery_name='SHARK_PhysicalChemical_2021_EXT_SMHI',
    )
