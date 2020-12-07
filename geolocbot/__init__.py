# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

# (!) the order of imports is not accidental
from geolocbot import exceptions, libs, _resources as resources, loaders, utils, searching, connecting
from geolocbot.utils import output

logging = loaders.fetch_logger()
searching.teryt.NameIDMaps = searching.teryt.NIMGet()
