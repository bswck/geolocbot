# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

__all__ = ('IdTranslation',)


class IdTranslation(object):
    def __init__(self, ID='', translation=''):
        self.ID = ID
        self.translation = translation

    def __getitem__(self, item): return getattr(self, item, '')
    def __repr__(self): return '_it(' + ', '.join(['%s=%r' % (k, v) for k, v in dict(self).items()]) + ')'
    def __str__(self): return str(self.ID) if self.ID else ''
    def __add__(self, other): return str(self.ID) if self.ID else '' + other

    def __iter__(self):
        yield 'ID', self.ID
        if self.translation != '':
            yield 'translation', self.translation
