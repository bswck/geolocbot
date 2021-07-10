""" Access the resources. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license
import os

import pandas as pd


class TerytData:
    _teryt_nts = None
    _teryt_simc = None
    _teryt_terc = None

    _dirname = os.path.dirname(__file__)
    _pandas_args = {
        'sep': ';',
        'dtype': 'str',
        'encoding': 'utf-8',
    }

    @classmethod
    def get_nts(cls) -> pd.DataFrame:
        if not cls._teryt_nts:
            cls._teryt_nts = pd.read_csv(
                os.path.join(cls._dirname, '../data/nts.csv'),
                **cls._pandas_args
            )
        return cls._teryt_nts

    @classmethod
    def get_simc(cls) -> pd.DataFrame:
        if not cls._teryt_simc:
            cls._teryt_simc = pd.read_csv(
                os.path.join(cls._dirname, '../data/simc.csv'),
                **cls._pandas_args
            )
        return cls._teryt_simc

    @classmethod
    def get_terc(cls) -> pd.DataFrame:
        if not cls._teryt_terc:
            cls._teryt_terc = pd.read_csv(
                os.path.join(cls._dirname, '../data/terc.csv.csv'),
                **cls._pandas_args
            )
        return cls._teryt_terc
