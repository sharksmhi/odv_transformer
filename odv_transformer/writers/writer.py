#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-03 14:33

@author: johannes
"""
from odv_transformer.utils import thread_process
from abc import abstractmethod, ABC
import numpy as np


def write_with_numpy(*args, **kwargs):
    """Write numpy arrays or pd.Series to file.

    Args:
        data: array
        save_path (str): complete path to file
        fmt: format of file eg. '%s', '%f'
        encoding: eg. 'utf-8'
    """
    thread_process(np.savetxt, *args, **kwargs)


class WriterBase(ABC):
    """Base Class for writers."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.data_serie = None
        for key, item in kwargs.items():
            setattr(self, key, item)

    @abstractmethod
    def write(self, *args, **kwargs):
        """Write."""
        raise NotImplementedError

    def _write(self, *args, **kwargs):
        """Write."""
        raise NotImplementedError
