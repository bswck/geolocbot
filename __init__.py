""" Geoloc-Bot. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import os

if not os.path.isfile('geolocbot.conf'):
    with open('geolocbot.conf', 'w+') as conf:
        dfconfig = "[wiki]\ntarget_wiki_login=StimBOT\nwikidata_login=Stim pl\n\n[logging]\nfilename=" \
                   "geolocbot.log\nencoding = utf-8\nformat = %%(asctime)-25s %%(name)-9s %%(levelname)-9s %%(" \
                   "message)s\ndatefmt = [%%Y-%%m-%%d]  %%H:%%M:%%S\nlevel = logging.DEBUG\n\n[pandas]\nsep = " \
                   ";\ndtype = str\nencoding = utf-8"
        conf.write(dfconfig)


if __name__ == '__main__':
    raise RuntimeError('run ./geolocbot/bot.py, not ./geolocbot/__init__.py')
else:
    # noinspection PyUnresolvedReferences
    from .bot import *

del os
