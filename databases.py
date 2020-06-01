# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3
# This is a cool tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default

import pywikibot as pwbot
import pandas as pd
from errors import Error
from pywikibot import pagegenerators as pg

class TooManyRows(Error):
    """Raised when too many rows appear in the table as an answer"""
    pass


simc = pd.read_csv("SIMC.csv", sep=';',
                   usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM'])
tercbase = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])
# with open('symquery.rq', 'r') as query_file:
#     QUERY = query_file.read()

# wikidata_site = pwbot.Site("wikidata", "wikidata")
# generator = pg.WikidataSPARQLPageGenerator(QUERY, site=wikidata_site)
# print(generator)

def terencode(data):
    global fromindex
    data = pd.DataFrame(data, index=[0])
    dcols = data.columns.tolist()

    if dcols == ['NAZWA']:
        teryt = {'NAZWA': data.at[0, 'NAZWA']}
        teryt = pd.DataFrame(teryt, index=[0])
        return teryt

    datac = data.copy()
    dname = datac.at[0, 'NAZWA']

    if dname.find(" (") != -1:
        for i in dname:

            if i == '(':
                fromindex = dname.find(i) - 1

        # deleting annotation, eg. '(województwo śląskie)'
        dname = dname.replace(dname[fromindex::], '')

    teryt = {'NAZWA': dname}  # {name: pagename}
    woj = data.at[0, 'województwo']
    wojewodztwa = tercbase.loc[(tercbase['NAZWA_DOD'] == 'województwo') & (tercbase['NAZWA'] == woj)]
    windex = wojewodztwa.index.tolist()
    teryt1 = {'WOJ': tercbase.at[windex[0], 'WOJ']}
    teryt.update(teryt1)
    cols = data.columns.tolist()

    if 'powiat' in cols:
        pot = data.at[0, 'powiat']
        if pot.find(" (") != -1:
            for i in pot:

                if i == '(':
                    fromindex = pot.find(i) - 1

            # deleting annotation, eg. '(województwo śląskie)'
            pot = pot.replace(pot[fromindex::], '')
        powiaty = tercbase.loc[(tercbase['NAZWA_DOD'] == 'powiat') & (tercbase['NAZWA'] == pot) & (
                tercbase['WOJ'] == tercbase.at[windex[0], 'WOJ'])]

        if powiaty.empty:
            powiaty = tercbase.loc[
                ((tercbase['NAZWA_DOD'] == 'powiat') & (tercbase['NAZWA'] == pot))]

        pindex = powiaty.index.tolist()
        teryt2 = {'POW': tercbase.at[pindex[0], 'POW']}
        teryt.update(teryt2)

        if 'gmina' in cols:
            gmi = data.at[0, 'gmina']

            if gmi.find(" (") != -1:
                for i in gmi:

                    if i == '(':
                        fromindex = gmi.find(i) - 1

                # deleting annotation, eg. '(województwo śląskie)'
                gmi = gmi.replace(gmi[fromindex::], '')
            gminy = tercbase.loc[
                ((tercbase['NAZWA_DOD'] == 'gmina miejska') | (tercbase['NAZWA_DOD'] == 'obszar wiejski') | (
                        tercbase['NAZWA_DOD'] == 'gmina wiejska') | (
                         tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                        tercbase['NAZWA'] == gmi) & (
                        tercbase['POW'] == tercbase.at[pindex[0], 'POW'])]

            if gminy.empty:

                gminy = tercbase.loc[
                    ((tercbase['NAZWA_DOD'] == 'gmina miejska') | (tercbase['NAZWA_DOD'] == 'obszar wiejski') | (
                            tercbase['NAZWA_DOD'] == 'gmina wiejska') | (
                             tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                            tercbase['NAZWA'] == gmi) & (
                            tercbase['POW'] == tercbase.at[windex[0], 'WOJ'])]

                if gminy.empty:
                    gminy = tercbase.loc[
                        ((tercbase['NAZWA_DOD'] == 'gmina miejska') | (tercbase['NAZWA_DOD'] == 'obszar wiejski') | (
                                tercbase['NAZWA_DOD'] == 'gmina wiejska') | (
                                 tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                                tercbase['NAZWA'] == gmi)]

            gindex = gminy.index.tolist()
            teryt3 = {'GMI': tercbase.at[gindex[0], 'GMI']}
            teryt.update(teryt3)

    teryt = pd.DataFrame(teryt, index=[0])

    return teryt


def filtersimc(data):
    global tw
    global tp
    global tg

    i = 0

    if 'WOJ' in data:
        tw = int(data.at[0, 'WOJ'])
        i += 1

    if 'POW' in data:
        tp = int(data.at[0, 'POW'])
        i += 1

    if 'GMI' in data:
        tg = int(data.at[0, 'GMI'])
        i += 1

    nazwa = data.at[0, 'NAZWA']
    goal = simc.copy()

    if i == 3:
        goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw) & (simc['POW'] == tp) & (simc['GMI'] == tg)]

        if goal.empty:
            goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw) & (simc['POW'] == tp)]

            if goal.empty:
                goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw)]

                if goal.empty:
                    goal = simc.loc[(simc['NAZWA'] == nazwa)]

    elif i == 2:
        goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw) & (simc['POW'] == tp)]

        if goal.empty:
            goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw)]

            if goal.empty:
                goal = simc.loc[(simc['NAZWA'] == nazwa)]

    elif i == 1:
        goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw)]

        if goal.empty:
            goal = simc.loc[(simc['NAZWA'] == nazwa)]

    elif i == 0:
        goal = simc.loc[(simc['NAZWA'] == nazwa)]

    goal = goal[['NAZWA', 'SYM']].reset_index()

    if goal.shape[0] > 1:
        raise TooManyRows(goal[['NAZWA', 'SYM']])

    else:
        return goal[['NAZWA', 'SYM']]
