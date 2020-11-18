# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

__all__ = ('CodeTranslation',)


class CodeTranslation(object):
    def __init__(self, code='', translation=''):
        self.code = code
        self.translation = translation

    def __getitem__(self, item): return getattr(self, item, '')
    def __repr__(self): return '_ct(' + ', '.join(['%s=%r' % (k, v) for k, v in dict(self).items()]) + ')'
    def __str__(self): return str(self.code) if self.code else ''
    def __add__(self, other): return str(self.code) if self.code else '' + other

    def __iter__(self):
        yield 'code', self.code
        if self.translation != '':
            yield 'translation', self.translation
