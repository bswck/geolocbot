""" Geoloc-Bot exceptions. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license


class BotError(Exception):
    """ An error which occured when a Geoloc-Bot's snippet was called. """
    __slots__ = ('message',)

    def __init__(self, message):
        self.message = message
        super(BotError, self).__init__(message)

    def __bool__(self): return isinstance(self.message, str)


class ConfigurationSetupError(BotError):
    """ Raised when *loaders* could not validate configuration file. """


class TERYTError(BotError):
    """ Exception class of TERYT. """


class UnpackError(TERYTError):
    """ Raised when unpacking fails. """


class ResourceError(TERYTError):
    """ Raised e.g. if the field of TERYT is empty. """
