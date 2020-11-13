# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import geolocbot
sys = geolocbot.libs.sys
be_quiet = False


def do_nothing(): pass


class GetLogger(object):
    """ Equivalent for logging.getLogger() made for ``with`` statement syntax. """

    def __init__(self, name='geolocbot'): self.name = name
    def __enter__(self): return geolocbot.libs.logging.getLogger(self.name)
    def __exit__(self, exc_type, exc_val, exc_tb): pass


def nice_repr(clsn, **kwargs):
    kwargs = ' (' + ', '.join(['%s=%r' % (k, v) for k, v in kwargs.items()]) + ')' if kwargs else ''
    return '<%s%s>' % (clsn, kwargs)


def output(*data, level='info', sep=' ', file='stdout', log=True, get_logger='geolocbot'):
    """ Outputting function. """
    ensure(isinstance(file, str), 'file cannot be a %r object' % type(file).__name__)
    file = getattr(sys, file, sys.stdout)
    data = sep.join([str(dp) for dp in data])
    if log:
        with getLogger(name=get_logger) as handler:
            if isinstance(data, geolocbot.libs.pandas.DataFrame):
                data = data.replace('\n', f'\n{" " * 46}')
            getattr(handler, level, handler.info)(data)
    print(data, file=file) if not be_quiet else do_nothing()
    return data


def ensure(condition, m):
    """ Assert, but raising custom *Exception* objects. """
    import operator
    dferr, chx = geolocbot.exceptions.GeolocbotError, operator.or_
    if not condition:
        raise chx(dferr(m), m)
    return True


getLogger = GetLogger
