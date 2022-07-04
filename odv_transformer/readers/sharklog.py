#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-06-15 16:24

@author: johannes
"""
import sqlite3
import pandas as pd


def get_db_conn(path=None):
    """Return a database connection object."""
    path = path or r'C:\Arbetsmapp\datasets\PhysicalChemical\sharklog.db'
    return sqlite3.connect(path)


class LogReader:
    """Reader and handler for the SHARK log (physical and chemical data)."""

    def __init__(self, table=None):
        """Initialize."""
        self.table = table

    def get_data_for_seqno_list(self, seqno_list):
        """Return dataframe of information based on the given list of seqnos.

        Args:
            seqno_list (iterable): Sequence numbers
        """
        if not isinstance(seqno_list, list):
            seqno_list = list(seqno_list)

        list_str = f"""'{seqno_list[0]}'"""
        for seqno in seqno_list[1:]:
            list_str += f""",'{seqno}'"""

        conn = get_db_conn()
        return pd.read_sql(
            f"""select * from {
            self.table} where seqno in (""" + list_str + """)""",
            conn
        )


if __name__ == '__main__':
    db_hand = LogReader(table='sharkintlog')
    # df = db_hand.get_data_for_seqno(21)
    df = db_hand.get_data_for_seqno_list([21, 23525])
    # df = db_hand.get_data_for_key('1894_77_SZ_0001')
