""" Access the resources. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

try:
    from resources import cached_teryt
except ImportError:
    from ..resources import cached_teryt
cached_teryt = cached_teryt
