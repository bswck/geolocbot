""" Log in to Nonsensopedia and Wikidata. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license
import time

import pywikibot
import requests

from . import utils
from .wiki import *


def login(call=0):
    if call < 6:
        ww = WikiWrapper()
        try:
            ww.site.login()
            ww.wikidata.site.login()
            utils.output('Zalogowano')
        except (pywikibot.exceptions.FatalServerError, requests.exceptions.ConnectionError):
            time.sleep(2)
            login(call=call + 1)
    else:
        utils.output('5 razy próbowano zalogować, SystemExit -1')
        exit(-1)
