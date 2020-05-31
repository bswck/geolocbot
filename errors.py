# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3


class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass
