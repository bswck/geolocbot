# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot exceptions. """


class GeolocbotBaseException(Exception):
    __slots__ = ()


class GeolocbotError(GeolocbotBaseException):
    """ An error which occured when a Geoloc-Bot`s snippet was called. """
    def __init__(self, m): self.m = m
    def __or__(self, other): return self if isinstance(self.m, str) else other


class ConfigurationSetupError(GeolocbotError):
    """ Raised when loaders cannot validate configuration file. """


class TerytFieldError(GeolocbotError):
    """ Exception class of `_TerytEntry`. """


class ParserError(TerytFieldError):
    """ Raised when parser fails. """


class ResourceError(TerytFieldError):
    """ Raised if the field of `_TerytEntry` is empty. """
