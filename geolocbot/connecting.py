# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Connect + log in to Nonsensopedia wiki. """

from geolocbot import *


def login(call=0):
    if call < 6:
        _wiki = wiki.WikiWrapper()
        try:
            _wiki.site.login()
            _wiki.base.site.login()
            utils.output('Zalogowano')
        except (libs.pywikibot.exceptions.FatalServerError, libs.requests.exceptions.ConnectionError):
            libs.time.sleep(2)
            login(call=call + 1)
    else:
        utils.output('5 razy próbowano zalogować, SystemExit -1')
        exit(-1)
