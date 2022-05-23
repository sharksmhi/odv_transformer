#!/usr/bin/env python3
"""
Created on 2022-02-03 11:03

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
