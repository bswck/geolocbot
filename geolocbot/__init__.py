# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

# (!) the order of imports is not accidental
from geolocbot import exceptions, libs, _resources as resources, loaders, tools, searching, connecting

output, logging = tools.output, loaders.fetch_logger()
searching.teryt.NameIDMap = getattr(searching.teryt, '_NameIDMap')()
