# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import pywikibot as pwbot
from databases import cp

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl

# Dictionary storing the captured information.
captured = {}


# This function reviews a category and decides,
# whether it is needed or not.
def findcats(c, title):
    for i in range(0, len(c), 1):

        # Checks if the category contains "Gmina".
        if "Kategoria:Gmina " in c[i]:
            gmina = c[i].replace("Kategoria:Gmina ", "")  # (No need for namespace and type name).
            readcategories(c[i])
            add = {"gmina": gmina}
            captured.update(add)

        # Checks if the category contains "Powiat "; disclaiming category "Powiaty".
        elif "Kategoria:Powiat " in c[i]:
            powiat = c[i].replace("Kategoria:Powiat ", "")
            readcategories(c[i])
            add = {"powiat": powiat.lower()}
            captured.update(add)

        # Checks if the category contains "Województwo ".
        elif "Kategoria:Województwo " in c[i]:
            wojewodztwo = c[i].replace("Kategoria:Województwo ", "")
            add = {"województwo": wojewodztwo.upper()}
            captured.update(add)

        # Exceptions.
        elif "Kategoria:Ujednoznacznienia" in c[i]:
            raise ValueError('Podana strona to ujednoznacznienie.')

        elif "Kategoria:Dzielnic" in c[i] or "Kategoria:Osiedl" in c[i]:
            page = pwbot.Page(site, title)
            text = page.text
            if "dzielnic" in text[:100]:
                print('Uwaga: Artykuł prawdopodobnie dotyczy dzielnicy… (TooManyRows)')
            elif "osiedle" in text[:100]:
                print('Uwaga: Artykuł prawdopodobnie dotyczy osiedla… (TooManyRows)')

        # Reading the category of category if it's one of these below.
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
    line = {"NAZWA": title}
    captured.update(line)
    return captured
