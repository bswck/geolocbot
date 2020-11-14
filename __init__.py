# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

from geolocbot import *


def run():
    connecting.log_in()
    # test
    while True:
        x = input('Find in SIMC: ')
        re = searching.simc.search(equal=x, quiet=True)
        if re:
            print('\n', re.result, '\n', sep='')


if __name__ == '__main__':
    run()
