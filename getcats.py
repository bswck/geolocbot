# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# Not yet the end. ;)

import pywikibot as pwbot

site = pwbot.Site('pl', 'nonsensopedia') # we're on nonsa.pl

captured = {} # this dictionary will be updated with geolocalisation info;

def satisfy(var, key): # this adds captured from categories geolocalisation info
    add = {key : var}
    captured.update(add)

def findcats(c, title): # this reviews all the categories, chooses needed
    for i in range(0, len(c), 1):
        if c[i].find("Kategoria:Gmina ") != -1: # checks if the category contains "Gmina"
            gmina = c[i].replace("Kategoria:Gmina ", "") # no need for namespace name
            readcategories(c[i])
            satisfy(gmina, "gmina") # data
        elif c[i].find("Kategoria:Powiat ") != -1: # checks if the category contains "Powiat "; disclaiming category "Powiaty"
            powiat = c[i].replace("Kategoria:Powiat ", "")
            readcategories(c[i])
            satisfy(powiat.lower(), "powiat")
        elif c[i].find("Kategoria:Województwo ") != -1: # checks if the category contains "Gmina"
            wojewodztwo = c[i].replace("Kategoria:Województwo ", "")
            satisfy(wojewodztwo.upper(), "województwo")
        # i'm still laughing at that point ↓
        elif c[i].find("Kategoria:Ujednoznacznienia") != -1:
            return 0
        # reading the category of category if it's one of these below
        elif c[i].find("Kategoria:Miasta w") != -1 or c[i].find("Kategoria:" + title) != -1 or c[i].find("Kategoria:Powiaty w") != -1 or c[i].find("Kategoria:Gminy w") != -1:
            readcategories(c[i])
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
    if len(title) == 0:
        return 0
    readcategories(title) # script starts
    if withkeypagename(title) == {'NAZWA' : title}:
        return 1
    elif withkeypagename(title) == {}:
        return 2
    else:
        return withkeypagename(title)

def withkeypagename(title):
    line = {"NAZWA" : title} # added key with pagename
    captured.update(line)
    return captured # returns the dictionary
