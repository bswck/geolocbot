# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

"""
TODO: Update this docstring.
Loads buffers for pandas.DataFrame objects (using configurations in *.conf file in this dir) from cached TERYT
register databases.

Variables `simc_csv', `terc_csv' and `nts_csv' contain raw text of *.csv databases from the Polish TERYT register.
    * SIMC and TERC are databases included in the TERYT register which is the National Official Register of the
      Territorial Division of the Country.
    * NTS was a classification of territorial units for referencing the subdivisions of countries for statistical
      purposes in Poland. Outdated since 2017 (important: do not confuse with NUTS geocode standard). Occurs as a
      pandas.DataFrame object in resources due to its occurences in Wikidata.

**Refs**
    * For more about TERYT (including SIMC and TERC), see:
        (en) http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default
        (pl) ⤵
        http://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/informacje_podstawowe/informacje_podstawowe.aspx?contrast=default
        (pl) https://pl.wikipedia.org/wiki/TERYT
    * For more about NTS, see:
        (pl) https://pl.wikipedia.org/wiki/NTS_(klasyfikacja)
    * For more about NUTS, see:
        (en) https://en.wikipedia.org/wiki/Nomenclature_of_Territorial_Units_for_Statistics
        (pl) https://pl.wikipedia.org/wiki/NUTS
"""

__all__ = ('buffers',)

from ._cached_csv import (
    simc_csv,
    terc_csv,
    nts_csv
)

buffers = {
    'simc': simc_csv,
    'terc': terc_csv,
    'nts': nts_csv
}
