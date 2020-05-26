# -*- coding: utf-8 -*-
# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# Not yet the end. ;)

import pywikibot as pwbot

site = pwbot.Site('pl', 'nonsensopedia') # we're on nonsa.pl

gotten = {} # this dictionary will be updated with geolocalisation info;
            # then repaired (it looks repulsive in the end).

def satisfy(var, key): # this adds geolocalisation info
    add = {key : var}
    gotten.update(add)

def findcats(c, title, tvftitle): # this reviews all the categories, chooses needed
    for i in range(0, len(c), 1):
        if c[i].find("Kategoria:Gmina ") != -1: # checks if the category contains "Gmina"
            gmina = c[i].replace("Kategoria:", "") # no need for namespace name
            readcategories(c[i], tvftitle)
            satisfy(gmina, "GMI") # data
        elif c[i].find("Kategoria:Powiat ") != -1: # checks if the category contains "Powiat "; disclaiming category "Powiaty"
            powiat = c[i].replace("Kategoria:", "")
            readcategories(c[i], tvftitle)
            satisfy(powiat, "POW")
        elif c[i].find("Kategoria:Województwo ") != -1: # checks if the category contains "Gmina"
            wojewodztwo = c[i].replace("Kategoria:", "")
            satisfy(wojewodztwo, "WOJ")
        # i'm still laughing at that point ↓
        elif c[i].find("Kategoria:Ujednoznacznienia") != -1:
            return 0
        # reading the category of category if it's one of these below
        elif c[i].find("Kategoria:Miasta w") != -1:
            readcategories(c[i], tvftitle)
        elif c[i].find("Kategoria:" + title) != -1:
            readcategories(c[i], tvftitle)
        elif c[i].find("Kategoria:Powiaty w") != -1:
            readcategories(c[i], tvftitle)
        elif c[i].find("Kategoria:Gminy w") != -1:
            readcategories(c[i], tvftitle)
        else:
            i += 1


def readcategories(title, tvftitle):
    c = [
        cat.title()
        for cat in pwbot.Page(site, title).categories()
        if 'hidden' not in cat.categoryinfo
    ]
    findcats(c, title, tvftitle)
    return c

def run(title):
    tvftitle = title # store the very first title
    readcategories(title, tvftitle) # script starts
    if withkeypagename(tvftitle) == {'NAZWA' : tvftitle}:
        noeffect = "Błąd: Zwrócono wartość początkową: '" + tvftitle + "'."  # returned for no-effect queries
        return noeffect
    elif withkeypagename(tvftitle) == {}:
        impossible = "Błąd: Nie rozpoznano wartości początkowej '" + tvftitle + "'." # returned for impossible/unreadable queries
        return impossible
    else:
        return withkeypagename(tvftitle)

def withkeypagename(tvftitle):
    line = {"NAZWA" : tvftitle} # added key with pagename
    gotten.update(line)
    return gotten # returns the dictionary

