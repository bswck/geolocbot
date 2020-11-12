# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Connect + log in to Nonsensopedia wiki. """

from scripts.userscripts.geolocbot import geolocbot
import requests.exceptions
import pywikibot


def log_in(*__a, _call=0):
    """ Log in, etc. """
    if _call < 6:
        from pywikibot.login import LoginStatus
        try:
            if LoginStatus.NOT_LOGGED_IN:
                pywikibot.Site('pl', 'nonsensopedia').login()
                geolocbot.output('Logged in, continuing')
            else:
                geolocbot.output('Already logged in, continuing')
        except (geolocbot.libs.pywikibot.exceptions.FatalServerError, requests.exceptions.SSLError):
            _call += 1
            geolocbot.libs.time.sleep(2)
            log_in(*__a, _call=_call)
    else:
        geolocbot.output('Attempted to log in 5 times, failed. Raising SystemExit with code -1.')
        exit(-1)


if __name__ == '__main__':
    log_in()
