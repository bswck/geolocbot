# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import sys


class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass


class TooManyRows(Error):
    """Raised when no pagename has been provided"""
    pass


def tmr():
    try:
        raise TooManyRows

    except TooManyRows:
        print("(nonsa.pl) Błąd: Więcej niż 1 rząd w odebranej tabeli.")
        sys.exit()
