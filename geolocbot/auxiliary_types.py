# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

__all__ = ('TranslatableValue',)


class TranslatableValue(object):
    def __init__(self, raw='', translation=''):
        self.raw = raw
        self.translation = translation

    def __getitem__(self, item): return getattr(self, item, NotImplemented)
    def __repr__(self): return repr(dict(self))
    def __str__(self): return str(self.raw) if self.raw else ''
    def __add__(self, other): return str(self.raw) if self.raw else '' + other

    def __iter__(self):
        yield 'raw', self.raw
        if self.translation != '':
            yield 'translation', self.translation
