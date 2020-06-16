# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import pywikibot as pwbot
import sys
from databases import cp
from querying import changemode

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl

# Dictionary storing the captured information.
captured = {}
p = []


# This function reviews a category and decides,
# whether it is needed or not.
def findcats(c, title):
    for i in range(0, len(c), 1):
        page = pwbot.Page(site, title)
        text = page.text

        if "osiedl" in text[:250] or "dzielnic" in text[:250]:
            if p == []:
                changemode(1)
                print()
                print("-" * (73 // 2) + "UWAGA!" + "-" * ((73 // 2) + 1))
                print('(nonsa.pl) [TooManyRows]: Artykuł prawdopodobnie dotyczy osiedla lub dzielnicy.')
                print("-" * 79)
                print()
                p.append(' ')

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

        # Reading the category of category if it's one of these below.
        elif "Kategoria:Miasta w" in c[i] or "Kategoria:Powiaty w" in c[i] or "Kategoria:Gminy w" in c[i] or \
                "Kategoria:" + title in c[i]:
            readcategories(c[i])

        elif cp('powiat', c[i]) is not False:
            powiat = cp('powiat', c[i])
            add = {"powiat": powiat}
            captured.update(add)

        elif cp('gmina', c[i]) is not False:
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
    page = pwbot.Page(site, title)
    text = page.text

    if text == '':
        raise KeyError('Nie ma takiej strony. [bot]')

    elif page.isRedirectPage():
        print('[bot] To jest przekierowanie.')
        title = str(page.getRedirectTarget()).replace('[[', '') \
                                             .replace(']]', '') \
                                             .replace('nonsensopedia:', '') \
                                             .replace('pl:', '')

        if '#' in title:
            for char in title:

                if char == '#':
                    sharpindex = title.find(char)
                    title = title[:sharpindex]

        print('[bot] Cel przekierowania to [[' + str(title) + ']].')

    readcategories(title)  # script starts
    return withkeypagename(title)


def withkeypagename(title):
    line = {"NAZWA": title}
    captured.update(line)
    return captured
