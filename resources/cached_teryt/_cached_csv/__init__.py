# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Includes cached databases. """

# noinspection PyUnresolvedReferences
from ._cached_simc import simc_csv  # PyCharm: file size (5,62 MB) too big (> 2,56 MB), disabled code insight feautures
from ._cached_terc import terc_csv
from ._cached_nts import nts_csv
