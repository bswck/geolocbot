# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license
#

# (!) the order of imports is not accidental
from scripts.userscripts.geolocbot.geolocbot import connecting, libs, loaders, resources, searching, tools

output, logging = tools.output, loaders.fetch_logger()

if __name__ == '__main__':
    libs.warnings.filterwarnings(action='ignore')
    tools.be_quiet = False
    w: libs.pandas.DataFrame = searching.terc_search.search(function='województwo', matchcase=True)

    # connecting.log_in()
