# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Connect + log in to Nonsensopedia wiki. """

from geolocbot.searching.wiki import *


def login(call=0):
    if call < 6:
        try:
            wiki.site.login()
            wiki.data_repo.login()
            geolocbot.output('Successfully logged in.')
        except (pywikibot.exceptions.FatalServerError, requests.exceptions.ConnectionError):
            time.sleep(2)
            login(call=call + 1)
    else:
        geolocbot.output('Attempted to log in 5 times, failed. Raising SystemExit with code -1.')
        exit(-1)
