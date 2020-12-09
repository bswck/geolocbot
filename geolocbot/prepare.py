# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Prepare the bot to start. """

__all__ = ('bot_config', 'logger', 'resources')

import geolocbot
import resources
from geolocbot import utils

abscd = geolocbot.libs.os.path.abspath(geolocbot.libs.os.path.curdir[0])
cfparser = geolocbot.libs.configparser.ConfigParser()


def _validate_configuration_file(fname='geolocbot.conf'):
    """ Checks whether the configuration file is valid to be evaluated. """
    dirpath, fname = abscd, fname
    fpath = geolocbot.libs.os.path.join(dirpath, fname)
    _msgs = {
        'missing-file': 'missing configuration file: {0} in {1}'.format(fname, dirpath),
        'missing-section': 'no section %r in configuration file: ' + fpath,
        'missing-option': 'no option %r in configuration file: ' + fpath,
    }
    required_sections = ('logging', 'pandas', 'wiki')
    required_options = {
        'logging': ('filename', 'encoding', 'format', 'datefmt', 'level'),
        'pandas': ('sep', 'dtype', 'encoding'),
        'wiki': ('target_wiki_login', 'wikidata_login')
    }

    assert geolocbot.libs.os.path.isfile(fpath), geolocbot.exceptions.ConfigurationSetupError(_msgs['missing-file'])
    cfparser.read(fpath)
    for section in required_sections:
        assert section in cfparser.sections(), \
            geolocbot.exceptions.ConfigurationSetupError(_msgs['missing-section'] % section)

    for section, options in required_options.items():
        for option in options:
            assert option in cfparser.options(section=section), \
                geolocbot.exceptions.ConfigurationSetupError(_msgs['missing-option'] % option)

    return True


conf = _validate_configuration_file()


def logger():
    """ Fetches the Geoloc-Bot`s logger. """
    # Could use logging.config.fileConfig() but pointless for further use
    logging_basic_config = {
        'filename': geolocbot.libs.os.path.join(abscd, cfparser.get('logging', 'filename')),
        'encoding': cfparser.get('logging', 'encoding'),
        'format': cfparser.get('logging', 'format'),
        'datefmt': cfparser.get('logging', 'datefmt'),
        'level': eval('geolocbot.libs.' + cfparser.get('logging', 'level'))
    }
    logging = geolocbot.libs.logging
    from geolocbot.libs import pywikibot
    logging.disable(level=pywikibot.logging.VERBOSE)
    with utils.get_logger('requests') as req:
        req.setLevel(logging.CRITICAL)
    logging.basicConfig(**logging_basic_config)
    with utils.get_logger('geolocbot') as geolocbot_logger:
        return geolocbot_logger


def teryt_resources(buffers: dict):
    """ Fetches pandas.DataFrame objects from cached TERYT. """
    pdconfkwds = {
        'sep': cfparser.get(section='pandas', option='sep'),
        'dtype': cfparser.get(section='pandas', option='dtype'),
        'encoding': cfparser.get(section='pandas', option='encoding')
    }

    def assign():
        resources.cached_teryt.simc = geolocbot.libs.pandas.read_csv(filepath_or_buffer=buffers['simc'], **pdconfkwds)
        resources.cached_teryt.terc = geolocbot.libs.pandas.read_csv(filepath_or_buffer=buffers['terc'], **pdconfkwds)
        resources.cached_teryt.nts = geolocbot.libs.pandas.read_csv(filepath_or_buffer=buffers['nts'], **pdconfkwds)

    assign()


def bot_config():
    """ Fetches the bot configuration. """
    return {
        'user': cfparser.get(section='wiki', option='target_wiki_login'),
        'wikidata-user': cfparser.get(section='wiki', option='wikidata_login')
    }


def argparser():
    import argparse
    _argparser = argparse.ArgumentParser()
    _argparser.add_argument('--page', nargs='?', const='', default='', help='Name of the page to be geolocated.')
    _argparser.add_argument(
        '--cat', nargs='?', const='', default='', help='Name of the category with pages to be geolocated.'
    )
    _argparser.add_argument('--shut_up', help='Whether the bot should be quiet.', action='store_true')
    _argparser.add_argument(
        '--no_wiki_login', default=False, help='Whether to log in before performing tasks.', action='store_true'
    )
    _argparser.add_argument(
        '--dont_log', default=False, help='Whether to log messages from Geolocbot.', action='store_true'
    )
    _argparser.add_argument(
        '--errpage', const='errpage',
        default='User:Stim/geolocbot/błędy', help='Name of the page for error reporting.', action='store_const'
    )
    _argparser.add_argument(
        '--postponepage', const='postponepage',
        default='User:Stim/geolocbot/przejrzeć', help='Name of the page for error reporting.', action='store_const'
    )
    _argparser.add_argument(
        '--debug', default=False, help='Turn on debugging mode.', action='store_true'
    )
    return _argparser


teryt_resources(buffers=resources.cached_teryt.buffers)
geolocbot.logging = logger()
