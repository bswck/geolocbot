# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

# (!) the order of imports is not accidental
from geolocbot import auxiliary_types, exceptions, libs, _resources as resources, loaders, tools, searching, connecting

output, logging, tools.be_quiet = tools.output, loaders.fetch_logger(), False
searching.teryt.IdTable = getattr(searching.teryt, '_IdTable')()
tools.be_quiet = True
