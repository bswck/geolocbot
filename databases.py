# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# This is a cool (yet buggy) tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default

import pandas as pd

simc = pd.read_csv("SIMC_2020-05-25.csv", sep=';', na_values=['-'], usecols=['WOJ', 'POW', 'GMI', 'NAZWA'])
tercbase = pd.read_csv("TERC_2020-05-25.csv", sep=';', na_values=['-'],
                       usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])


def fill(value, teryt):  # as in other files, filling in the dictionary
    teryt.update(value)


def terencode(data):
    if str(data).find("ERROR") != -1:
        return "<+Fiodorr> Błąd! Gratulacje!"
    data = pd.DataFrame(data, index=[0])
    teryt = {'NAZWA': data.at[0, 'NAZWA']}  # {name: pagename}
    woj = data.at[0, 'województwo']
    wojewodztwa = tercbase.loc[(tercbase['NAZWA_DOD'] == 'województwo') & (tercbase['NAZWA'] == woj)]
    windex = wojewodztwa.index.tolist()
    teryt1 = {'WOJ': tercbase.at[windex[0], 'WOJ']}
    fill(teryt1, teryt)
    if 'powiat' in data.columns:
        pot = data.at[0, 'powiat']
        powiaty = tercbase.loc[(tercbase['NAZWA_DOD'] == 'powiat') & (tercbase['NAZWA'] == pot)]
        pindex = powiaty.index.tolist()
        teryt2 = {'POW': tercbase.at[pindex[0], 'POW']}
        fill(teryt2, teryt)
        if 'gmina' in data.columns:
            gmi = data.at[0, 'gmina']
            # I hate that there are mountains (3) of municipalities.
            gminy = tercbase.loc[((tercbase['NAZWA_DOD'] == 'gmina miejska') | (
                        tercbase['NAZWA_DOD'] == 'gmina wiejska') | (
                                              tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                                             tercbase['NAZWA'] == gmi)]
            gindex = gminy.index.tolist()
            teryt3 = {'GMI': tercbase.at[gindex[0], 'GMI']}
            fill(teryt3, teryt)
    return teryt


def filtersimc(data):
    if str(data).find("Błąd") != -1:
        return "<+Fiodorr> A próbowałeś Emacsem przez sendmail?"  # XD
    else:
        data = pd.DataFrame(data, index=[0])
        return data
