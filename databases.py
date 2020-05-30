# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3
# This is a cool tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default

import pandas as pd

simc = pd.read_csv("SIMC_2020-05-25.csv", sep=';',
                   usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM', 'SYMPOD'])
tercbase = pd.read_csv("TERC_2020-05-25.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])


def terencode(data):
    if str(data).find("ERROR") != -1:
        return "<+Fiodorr> Błąd! Gratulacje!"

    data = pd.DataFrame(data, index=[0])
    teryt = {'NAZWA': data.at[0, 'NAZWA']}  # {name: pagename}
    woj = data.at[0, 'województwo']
    wojewodztwa = tercbase.loc[(tercbase['NAZWA_DOD'] == 'województwo') & (tercbase['NAZWA'] == woj)]
    windex = wojewodztwa.index.tolist()
    teryt1 = {'WOJ': tercbase.at[windex[0], 'WOJ']}
    teryt.update(teryt1)

    if 'powiat' in data.columns:
        pot = data.at[0, 'powiat']
        powiaty = tercbase.loc[(tercbase['NAZWA_DOD'] == 'powiat') & (tercbase['NAZWA'] == pot)]
        pindex = powiaty.index.tolist()
        teryt2 = {'POW': tercbase.at[pindex[0], 'POW']}
        teryt.update(teryt2)

        if 'gmina' in data.columns:
            gmi = data.at[0, 'gmina']
            gminy = tercbase.loc[((tercbase['NAZWA_DOD'] == 'gmina miejska') | (
                    tercbase['NAZWA_DOD'] == 'gmina wiejska') | (
                                          tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                                         tercbase['NAZWA'] == gmi)]
            gindex = gminy.index.tolist()
            teryt3 = {'GMI': tercbase.at[gindex[0], 'GMI']}
            teryt.update(teryt3)

    keys = list(teryt.keys())
    teryt = pd.DataFrame(teryt, index=[0])
    return teryt, keys


def filtersimc(data, keys):

    if str(data).find("Błąd") != -1:
        # XD
        return "<+Fiodorr> A próbowałeś Emacsem przez sendmail?"

    i = 0

    if 'WOJ' in keys:
        tw = int(data.at[0, 'WOJ'])
        i += 1

    if 'POW' in keys:
        tp = int(data.at[0, 'POW'])
        i += 1

    if 'GMI' in keys:
        tg = int(data.at[0, 'GMI'])
        i += 1

    nazwa = data.at[0, 'NAZWA']

    # Here to do!
    goal = simc.loc[(simc['NAZWA'] == nazwa) & (simc['WOJ'] == tw) & (simc['POW'] == tp) & (simc['GMI'] == tg)]
    goalindex = goal.index.tolist()

    return goalindex[0]
