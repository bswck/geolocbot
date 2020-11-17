# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

from geolocbot import *


def parse(string):
    args = string.split('  ')
    keys = [arg[:arg.index('=')] for arg in args]
    values = [True if arg[arg.index('=')+1:] == 'True' else arg[arg.index('=')+1:] for arg in args]
    return dict(zip(keys, values))


def run():
    terc = searching.teryt.terc
    x = input('Wskazówki do wyszukiwania w TERC: ')
    while not x or x.isspace():
        x = input('Wskazówki do wyszukiwania w TERC: ')
    terc_result = terc.search(**parse(x))
    print(terc_result)
    print('\n\nWyniki wyszukiwania w bazie TERC:', terc_result.results, sep='\n')
    y = terc_result.transfer('simc')
    print('\n\nWyniki transferu wyszukiwania z TERC do SIMC:', y, '\n', sep='\n')


if __name__ == '__main__':
    run()
