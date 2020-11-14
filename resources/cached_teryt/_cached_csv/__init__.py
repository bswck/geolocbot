# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Includes cached databases. """

import os
terc_csv = open(os.path.join(__path__[0], '_cached_terc.csv'), encoding='utf-8')
simc_csv = open(os.path.join(__path__[0], '_cached_simc.csv'), encoding='utf-8')
nts_csv = open(os.path.join(__path__[0], '_cached_nts.csv'), encoding='utf-8')
