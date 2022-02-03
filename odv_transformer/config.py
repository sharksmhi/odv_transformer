#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 17:59

@author: johannes
"""
import json
import yaml
from copy import deepcopy
from pathlib import Path
from odv_transformer import utils


class Settings:
    """Config class.

    Keep track of available settings.
    """

    def __init__(self):
        """Initiate settings object."""
        self.base_directory = utils.get_base_folder()
        self.user = Path.home().name
        self.readers = {}
        self.writers = {}

        self._load_settings(self.base_directory.joinpath('etc'))

    def _load_settings(self, etc_path):
        """Load settings."""
        settings = {}
        for fid in etc_path.glob('**/*.yaml'):
            with open(fid, encoding='utf8') as fd:
                content = yaml.load(fd, Loader=yaml.FullLoader)
                settings[str(fid)] = content

        for fid in etc_path.glob('**/*.json'):
            with open(fid, 'r') as fd:
                content = json.load(fd)
                settings[str(fid)] = content

        self.set_attributes(self, **settings)

    def load_reader(self, reader):
        """Return reader instance."""
        reader_instance = self.readers[reader].get('reader')
        return reader_instance(**deepcopy(self.readers.get(reader)))

    def load_writer(self, writer):
        """Return writer instance."""
        writer_instance = self.writers[writer].get('writer')
        return writer_instance(**deepcopy(self.writers.get(writer)))

    @property
    def list_of_readers(self):
        """Return list of readers names."""
        return list(self.readers)

    @property
    def list_of_writers(self):
        """Return list of writers names."""
        return list(self.writers)

    @staticmethod
    def set_attributes(obj, **kwargs):
        """Set attribute to object."""
        for key, value in kwargs.items():
            setattr(obj, key, value)

    def __setattr__(self, name, value):
        """Define the setattr for object self.

        Special management of readers and writers.
        """
        if Path(name).is_file():
            if isinstance(value, dict) and \
                    ('readers' in name or 'writers' in name):
                if 'readers' in name:
                    utils.recursive_dict_update(
                        self.readers, {Path(name).stem: value}
                    )
                else:
                    utils.recursive_dict_update(
                        self.writers, {Path(name).stem: value}
                    )
            else:
                super().__setattr__(Path(name).stem, value)
        else:
            super().__setattr__(name, value)


if __name__ == "__main__":
    s = Settings()
