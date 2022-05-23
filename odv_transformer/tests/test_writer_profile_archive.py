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

    arch_path = Path(
        r'C:\Arbetsmapp\datasets\Profile\2021\SHARK_Profile_2021_COD_SMHI')
    s.read(
        str(arch_path),
        reader='profile',
        delivery_name=arch_path.name,
    )

    s.write(
        writer='ices_profile',
        delivery_name=arch_path.name,
        file_name=arch_path.name.lower(),
    )
