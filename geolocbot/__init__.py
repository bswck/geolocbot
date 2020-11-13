# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license
#

# (!) the order of imports is not accidental
from geolocbot import exceptions, libs, _resources as resources, loaders, connecting, tools, searching

output, logging = tools.output, loaders.fetch_logger()

if __name__ == '__main__':
    """ Do the stuff """
