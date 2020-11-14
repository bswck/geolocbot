# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Prepare the bot to start. """

from geolocbot import exceptions, libs, tools
import resources

abscd = libs.os.path.abspath(libs.os.path.curdir[0])
cfparser = libs.configparser.ConfigParser()


def _validate_configuration_file(fname='geolocbot.conf'):
    """ Checks whether the configuration file is valid to be evaluated. """
    dirpath, fname, require = abscd, fname, tools.ensure
    fpath = libs.os.path.join(dirpath, fname)
    _msgs = {
        'missing-file': 'missing configuration file: {0} in {1}'.format(fname, dirpath),
        'missing-section': 'no section %r in configuration file: ' + fpath,
        'missing-option': 'no option %r in configuration file: ' + fpath,
    }
    required_sections = ('logging', 'pandas')
    required_options = {
        'logging': ('filename', 'encoding', 'format', 'datefmt', 'level'),
        'pandas': ('sep', 'dtype', 'encoding')
    }

    require(libs.os.path.isfile(fpath), exceptions.ConfigurationSetupError(_msgs['missing-file']))
    cfparser.read(fpath)
    for section in required_sections:
        require(
            section in cfparser.sections(), exceptions.ConfigurationSetupError(_msgs['missing-section'] % section)
        )
    for section, options in required_options.items():
        for option in options:
            require(
                option in cfparser.options(section=section),
                exceptions.ConfigurationSetupError(_msgs['missing-option'] % option)
            )
    return True


conf = _validate_configuration_file()


def fetch_logger():
    """ Fetches the Geoloc-Bot`s logger. """
    # Could use logging.config.fileConfig() but pointless for further use
    __loggingbasicConfig = {
        'filename': libs.os.path.join(abscd, cfparser.get('logging', 'filename')),
        'encoding': cfparser.get('logging', 'encoding'),
        'format': cfparser.get('logging', 'format'),
        'datefmt': cfparser.get('logging', 'datefmt'),
        'level': eval('libs.' + cfparser.get('logging', 'level'))
    }
    logging = libs.logging
    from geolocbot.libs import pywikibot
    logging.disable(level=pywikibot.logging.VERBOSE)
    with tools.getLogger('requests') as req:
        req.setLevel(logging.CRITICAL)
    logging.basicConfig(**__loggingbasicConfig)
    with tools.getLogger('geolocbot') as __geolocbot_logger:
        return __geolocbot_logger


def fetch_resources(buffers: dict):
    """ Fetches pandas.DataFrame objects from cached TERYT. """
    pdconfkwds = {
        'sep': cfparser.get(section='pandas', option='sep'),
        'dtype': cfparser.get(section='pandas', option='dtype'),
        'encoding': cfparser.get(section='pandas', option='encoding')
    }

    def assign():
        import resources
        resources.cached_teryt.simc = libs.pandas.read_csv(filepath_or_buffer=buffers['simc'], **pdconfkwds)
        resources.cached_teryt.terc = libs.pandas.read_csv(filepath_or_buffer=buffers['terc'], **pdconfkwds)
        resources.cached_teryt.nts = libs.pandas.read_csv(filepath_or_buffer=buffers['nts'], **pdconfkwds)

    assign()


fetch_resources(buffers=resources.cached_teryt.striobuffers)
