# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import pywikibot as pwbot
import sys
from __init__ import geolocbot
from databases import cp

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl

# Dictionary storing the captured information.
captured = {}
p = []
getcats_fors = []
be_careful = []


def cleanup_getcats():
    if captured != {}:
        for key_value in list(captured.keys()):
            del captured[key_value]

    while p != []:
            del p[0]

    while getcats_fors != []:
            del getcats_fors[0]

    while be_careful != []:
            del be_careful[0]



# This function reviews a category and decides,
# whether it is needed or not.
def findcats(c, title):
    for i in range(len(c)):
        getcats_fors.append(str(len(getcats_fors) + 1))
        page = pwbot.Page(site, title)
        text = page.text

        if "osiedl" in text[:250] or "dzielnic" in text[:250]:
            if p == []:
                print()
                geolocbot.output("-" * (73 // 2) + "UWAGA!" + "-" * ((73 // 2) + 1))
                geolocbot.output('(nonsa.pl) [TooManyRows]: Artykuł prawdopodobnie dotyczy osiedla lub dzielnicy.')
                geolocbot.output("-" * 79)
                print()
                p.append(' ')

        # Checks if the category contains "Gmina".
        if 'gmina' not in captured and "Kategoria:Gmina " in c[i]:
            geolocbot.debug.output('Sprawdzam gminę.')
            gmina = c[i].replace("Kategoria:Gmina ", "")  # (No need for namespace and type name).
            readcategories(c[i])
            add = {"gmina": gmina}
            captured.update(add)

        # Checks if the category contains "Powiat "; disclaiming category "Powiaty".
        elif 'powiat' not in captured and "Kategoria:Powiat " in c[i]:
            powiat = c[i].replace("Kategoria:Powiat ", "")
            readcategories(c[i])
            add = {"powiat": powiat.lower()}
            captured.update(add)

        # Checks if the category contains "Województwo ".
        elif 'województwo' not in captured and "Kategoria:Województwo " in c[i]:
            wojewodztwo = c[i].replace("Kategoria:Województwo ", "")
            add = {"województwo": wojewodztwo.upper()}
            captured.update(add)

        # Exceptions.
        elif "Kategoria:Ujednoznacznienia" in c[i]:
            raise ValueError('Podana strona to ujednoznacznienie. [b]')

        # Reading the category of category if it's one of these below.
        elif ("Kategoria:Miasta w" in c[i] or "Kategoria:Powiaty w" in c[i] or "Kategoria:Gminy w" in c[i] or \
                "Kategoria:" + title in c[i]) and ('powiat' not in captured or 'gmina' not in captured):

            if cp('powiat', title) is not False:
                powiat = cp('powiat', title)
                add = {"powiat": powiat}
                captured.update(add)

            if cp('gmina', title) is not False:
                gmina = cp('gmina', title)
                add = {"gmina": gmina}
                captured.update(add)

            readcategories(c[i])

        else:
            if c[i] not in be_careful:
                be_careful.append(c[i])
                readcategories(c[i])


def readcategories(title):
    c = [
        cat.title()
        for cat in pwbot.Page(site, title).categories()
        if 'hidden' not in cat.categoryinfo
    ]

    findcats(c, title)
    return c


def run(title):
    page = pwbot.Page(site, title)
    text = page.text

    if text == '':
        raise KeyError('Nie ma takiej strony. [b]')

    readcategories(title)  # script starts
    geolocbot.output('Ciekawostka: pętla for w funkcji findcats została wywołana ' + getcats_fors[-1] + \
                     ' razy w tym zapytaniu.')
    geolocbot.output('Z kategorii artykułu mam następujące dane:')
    geolocbot.output('województwo: {0}.'.format(
        (captured['województwo'].lower() if 'województwo' in list(captured.keys()) else '–')))
    geolocbot.output('powiat: {0}.'.format((captured['powiat'] if 'powiat' in list(captured.keys()) else '–')))
    geolocbot.output('gmina: {0}.'.format((captured['gmina'] if 'gmina' in list(captured.keys()) else '–')))
    return withkeypagename(title)


def withkeypagename(title):
    line = {"NAZWA": title}
    captured.update(line)
    return captured
