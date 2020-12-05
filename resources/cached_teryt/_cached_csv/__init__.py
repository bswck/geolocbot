# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Includes cached databases. """

import os

simc_path = os.path.join(__path__[0], '_cached_simc.csv')
terc_path = os.path.join(__path__[0], '_cached_terc.csv')
nts_path = os.path.join(__path__[0], '_cached_nts.csv')
encoding = 'utf-8'
assert all((os.path.isfile(file) for file in (simc_path, terc_path, nts_path))), 'missing resources at %s' % __path__[0]
simc_csv = open(simc_path, encoding=encoding)
terc_csv = open(terc_path, encoding=encoding)
nts_csv = open(nts_path, encoding=encoding)
