# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import pywikibot as pwbot
from databases import cp

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl

captured = {}  # this dictionary will be updated with geolocalisation info;


def findcats(c, title):  # this reviews all the categories, chooses needed
    for i in range(0, len(c), 1):

        # checks if the category contains "Gmina"
        if "Kategoria:Gmina " in c[i]:
            gmina = c[i].replace("Kategoria:Gmina ", "")  # no need for namespace name
            readcategories(c[i])
            add = {"gmina": gmina}
            captured.update(add)

        # checks if the category contains "Powiat "; disclaiming category "Powiaty"
        elif "Kategoria:Powiat " in c[i]:
            powiat = c[i].replace("Kategoria:Powiat ", "")
            readcategories(c[i])
            add = {"powiat": powiat.lower()}
            captured.update(add)

        # checks if the category contains "Województwo "
        elif "Kategoria:Województwo " in c[i]:
            wojewodztwo = c[i].replace("Kategoria:Województwo ", "")
            add = {"województwo": wojewodztwo.upper()}
            captured.update(add)

        # i'm still laughing at that point ↓
        elif c[i].find("Kategoria:Ujednoznacznienia") != -1:
            raise ValueError('Podana strona to ujednoznacznienie.')

        # reading the category of category if it's one of these below
        elif c[i].find("Kategoria:Miasta w") != -1 or c[i].find("Kategoria:" + title) != -1 or c[i].find(
                "Kategoria:Powiaty w") != -1 or c[i].find("Kategoria:Gminy w") != -1:
            readcategories(c[i])

        elif cp('powiat', c[i]) != False:
            powiat = cp('powiat', c[i])
            add = {"powiat": powiat}
            captured.update(add)

        elif cp('gmina', c[i]) != False:
            gmina = cp('gmina', c[i])
            add = {"gmina": gmina}
            captured.update(add)

        else:
            i += 1


def readcategories(title):
    c = [
        cat.title()
        for cat in pwbot.Page(site, title).categories()
        if 'hidden' not in cat.categoryinfo
    ]

    findcats(c, title)
    return c


def run(title):
    readcategories(title)  # script starts
    return withkeypagename(title)


def withkeypagename(title):
    line = {"NAZWA": title}  # added key with pagename
    captured.update(line)
    return captured  # returns the dictionary
