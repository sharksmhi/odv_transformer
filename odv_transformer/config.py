#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 17:59

@author: johannes
"""
import json
import yaml
from pathlib import Path
from odv_transformer import utils


class Settings:
    """Config class.

    Keep track of available settings.
    """

    def __init__(self):
        """Initiate settings object."""
        self.base_directory = utils.get_base_folder()
        self._load_settings(self.base_directory.joinpath('etc'))
        self.user = Path.home().name

    def _load_settings(self, etc_path):
        """Load settings."""
        settings = {}
        for fid in etc_path.glob('**/*.yaml'):
            with open(fid, encoding='utf8') as fd:
                content = yaml.load(fd, Loader=yaml.FullLoader)
                settings[fid.stem] = content

        for fid in etc_path.glob('**/*.json'):
            with open(fid, 'r') as fd:
                content = json.load(fd)
                settings[fid.stem] = content

        self.set_attributes(self, **settings)

    def set_attributes(self, obj, **kwargs):
        """Set attribute to object."""
        for key, value in kwargs.items():
            setattr(obj, key, value)


if __name__ == "__main__":
    s = Settings()
