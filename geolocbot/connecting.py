# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Connect + log in to Nonsensopedia wiki. """

import geolocbot
from geolocbot.libs import *


def log_in(*__a, _call=0):
    """ Log in, etc. """
    ucf = geolocbot.loaders.fetch_bot_config()
    nonsa = pywikibot.Site('pl', 'nonsensopedia', user=ucf['user'])
    wd = pywikibot.Site('wikidata', 'wikidata', user=ucf['wikidata_user'])
    if _call < 6:
        try:
            if not nonsa.logged_in:
                nonsa.login()
            if not wd.logged_in:
                wd.login()
            geolocbot.output('Successfully logged in.')
        except (pywikibot.exceptions.FatalServerError, requests.exceptions.SSLError):
            _call += 1
            geolocbot.libs.time.sleep(2)
            log_in(*__a, _call=_call)
    else:
        geolocbot.output('Attempted to log in 5 times, failed. Raising SystemExit with code -1.')
        exit(-1)
