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
            gmina = c[i].replace("Kategoria:Gmina ", "") # no need for namespace and category (already as key) name
            readcategories(c[i])
            satisfy(gmina, "GMI") # data
        elif c[i].find("Kategoria:Powiat ") != -1: # checks if the category contains "Powiat "; disclaiming category "Powiaty"
            powiat = c[i].replace("Kategoria:Powiat ", "")
            readcategories(c[i])
            satisfy(powiat.lower(), "POW")
        elif c[i].find("Kategoria:Województwo ") != -1: # checks if the category contains "Województwo "
            wojewodztwo = c[i].replace("Kategoria:Województwo ", "")
            satisfy(wojewodztwo.upper(), "WOJ") # it's characteristic for provinces in TERC and SIMC databases
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
    title = title[0].upper() + title[1::] # capitalize first letter
    readcategories(title) # script starts
    if withkeypagename(title) == {'NAZWA' : title}:
        return 0
    elif withkeypagename(title) == {}:
        return 1
    else:
        return withkeypagename(title)

def withkeypagename(title):
    line = {"NAZWA" : title} # added key with pagename
    captured.update(line)
    return captured # returns the dictionary

