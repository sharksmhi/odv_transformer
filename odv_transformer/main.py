#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-02-02 17:56

@author: johannes

ICES ODV template for data deliveries.
- https://www.ices.dk/data/data-portals/Pages/ocean-submit.aspx

"""
from odv_transformer.config import Settings
from odv_transformer.handler import DataFrames, MultiDeliveries


class Session:
    """Transform data into ODV-ICES format.

    Readability counts.
    """

    def __init__(self, *args, **kwargs):
        """Initialize and store the settings- and deliveries object."""
        self.settings = Settings()
        self.deliveries = MultiDeliveries()

    def read(self, file_path, *args, reader=None, delivery_name=None,
             data_type=None, **kwargs):
        """Read and append requested data delivery.

        Using the given reader (name of reader) to load and initialize
        a reader object via Settings. Elements of the data delivery are
        put into Frame objects and collected into a delivery dictionary.

        Args:
            file_path (str): Path to delivery
            reader (str): One of the readers found in
                          self.settings.list_of_readers
            delivery_name (str): Name of delivery
            data_type (str): Type of data, eg. physicalchemical,
                             CTD, tube sample chlorophyll
        """
        if not reader:
            raise ValueError(
                'Missing reader! Please give one as input '
                '(App.read(reader=NAME_OF_READER)'
            )
        if reader not in self.settings.list_of_readers:
            raise ValueError(
                'Given reader does not exist as a valid option! '
                '(valid options: {}'.format(
                    ', '.join(self.settings.list_of_readers)
                )
            )
        if not file_path:
            raise ValueError(
                'Missing file path! Please give one as input '
                '(App.read(PATH_TO_DATA_SOURCE)'
            )
        if not delivery_name:
            raise ValueError(
                'Missing delivery name! Please give one as input '
                '(App.read(delivery_name=NAME_OF_DELIVERY)'
            )

        reader = self.settings.load_reader(reader)
        reader.load(file_path, **kwargs)
        data_type = data_type or reader.get('data_type')

        dfs = DataFrames(data_type=data_type, name=delivery_name)
        for element, item in reader.elements.items():
            df = reader.read_element(item.pop('element_specifier'), **item)
            dfs.append_new_frame(name=element, data=df)

        self.deliveries.append_new_delivery(name=delivery_name, data=dfs)

    def write(self, *args, writer=None, delivery_name=None, **kwargs):
        """Write log.

        Using the given writer (name of writer) to load and
        initialize a writer object via Settings.

        Args:
            *args:
            writer (str): Using the given writer to write log to file.
                          Available writers can be found in
                          self.settings.list_of_writers
            delivery_name (str): Name of the delivery write
            **kwargs (dict): kwargs to pass on to writer
        """
        if not writer:
            raise ValueError(
                'Missing writer! Please give one as input '
                '(App.write(writer=NAME_OF_WRITER)'
            )
        if writer not in self.settings.list_of_writers:
            raise ValueError(
                'The given writer does not exist as a valid option! '
                '(valid options: {}'.format(
                    ', '.join(self.settings.list_of_writers)
                )
            )
        if not delivery_name:
            raise ValueError('Missing delivery name! Please give one as input!')

        writer = self.settings.load_writer(writer)
        kwargs.setdefault('default_file_name', writer.default_file_name)
        file_path = self.settings.get_export_file_path(**kwargs)

        if 'default_file_name' in kwargs:
            kwargs.pop('default_file_name')
        writer.write(
            file_path,
            self.deliveries.get(delivery_name),
            pmap=self.settings.parameter_mapping,
            **kwargs
        )
