# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Prepare the bot to start. """

__all__ = ('bot_config', 'logger')

import configparser
import os

import geolocbot
from . import utils

abscd = os.path.abspath(os.path.curdir[0])
cfparser = configparser.ConfigParser()


def _validate_configuration_file(fname='geolocbot.conf'):
    """ Checks whether the configuration file is valid to be evaluated. """
    dirpath, fname = abscd, fname
    fpath = os.path.join(dirpath, fname)
    _msgs = {
        'missing-file': 'missing configuration file: {0} in {1}'.format(fname, dirpath),
        'missing-section': 'no section %r in configuration file: ' + fpath,
        'missing-option': 'no option %r in configuration file: ' + fpath,
    }
    required_sections = ('logging', 'wiki')
    required_options = {
        'logging': ('filename', 'encoding', 'format', 'datefmt', 'level'),
        'wiki': ('target_wiki_login', 'wikidata_login')
    }

    utils.require(os.path.isfile(fpath), utils.ConfigurationSetupError(_msgs['missing-file']))
    cfparser.read(fpath)
    for section in required_sections:
        utils.require(section in cfparser.sections(),
                      utils.ConfigurationSetupError(_msgs['missing-section'] % section))

    for section, options in required_options.items():
        for option in options:
            utils.require(option in cfparser.options(section=section),
                          utils.ConfigurationSetupError(_msgs['missing-option'] % option))

    return True


conf = _validate_configuration_file()


def logger():
    """ Fetches the Geoloc-Bot`s logger. """
    # Could use logging.config.fileConfig() but pointless for further use
    logging_basic_config = {
        'filename': os.path.join(abscd, cfparser.get('logging', 'filename')),
         # Python 3.9: 'encoding': cfparser.get('logging', 'encoding'),
        'format': cfparser.get('logging', 'format'),
        'datefmt': cfparser.get('logging', 'datefmt'),
        'level': getattr(utils, cfparser.get('logging', 'level'), utils.logging.DEBUG)
    }
    logging = utils.logging
    logging.disable(level=utils.pywikibot.logging.VERBOSE)
    with utils.get_logger('requests') as req:
        req.setLevel(logging.CRITICAL)
    logging.basicConfig(**logging_basic_config)
    with utils.get_logger() as geolocbot_logger:
        return geolocbot_logger


def bot_config():
    """ Fetches the bot configuration. """
    return {
        'user': cfparser.get(section='wiki', option='target_wiki_login'),
        'wikidata-user': cfparser.get(section='wiki', option='wikidata_login')
    }


def argparser():
    """ Prepare command-line arguments parser. """
    import argparse
    deferpage = {'default': 'User:Stim/geolocbot/przejrzeć', 'help': 'name of the page for deferred pages reporting'}
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('--page', nargs='?', const='', default='', help='name of the page to be geolocated')
    arg('--cat', nargs='?', const='', default='', help='name of the category with pages to be geolocated')
    arg('--deferpage', nargs='?', const='', **deferpage)
    arg('--shut-up', help='mute the bot', action='store_true')
    arg('--no-wiki-login', default=False, help='do not log in to wiki before performing tasks', action='store_true')
    arg('--dont-log', default=False, help='do not log messages from Geolocbot', action='store_true')
    arg('--debug', default=False, help='turn on debugging mode', action='store_true')
    return parser


geolocbot.logging = logger()
