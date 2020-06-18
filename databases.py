# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
# This is a cool tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default.

import pywikibot as pwbot
import pandas as pd
import sys
from __init__ import geolocbot


class Error(Exception):
    """Base class for other exceptions"""
    pass


class TooManyRows(Error):
    """Raised when too many rows appear in the table as an answer"""
    pass


simc = pd.read_csv("SIMC.csv", sep=';',
                   usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM'])
tercbase = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])

globname = []
globterc = {}
globtercc = []
gapterc = []


def delapterc():
    del gapterc[0]


def updatename(name):
    if len(globname) >= 1:
        del globname[0]
    globname.append(name)
    geolocbot.output('Aktualizacja docelowego adresu: [[' + name + ']].')


# This function is checking exactly if a category
# without info at the beginning in its name
# as "powiat (…)", "gmina (…)" etc. isn't
# in fact a powiat or gmina.
# For example: "Warszawa". Warsaw is a city,
# but it's rights are as big as powiat's rights.
# That means that Warsaw's localities' powiat is just Warsaw.
def cp(typ, name):
    if typ == 'gmina':
        gmina = tercbase.loc[(tercbase['NAZWA'] == name) &
                             ((tercbase['NAZWA_DOD'] == 'gmina miejska') |
                              (tercbase['NAZWA_DOD'] == 'obszar wiejski') |
                              (tercbase['NAZWA_DOD'] == 'gmina wiejska') |
                              (tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska'))]
        if gmina.empty:
            return False

        else:
            gmina = gmina.reset_index()
            return gmina.at[0, 'NAZWA']

    elif typ == 'powiat':
        powiat = tercbase.loc[(tercbase['NAZWA'] == name) & (
                (tercbase['NAZWA_DOD'] == typ) | (tercbase['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

        if powiat.empty:
            return False

        else:
            powiat = powiat.reset_index()
            return powiat.at[0, 'NAZWA']

    else:
        x = tercbase.loc[(tercbase['NAZWA'] == name) & (
                (tercbase['NAZWA_DOD'] == 'powiat') | (tercbase['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

        if not x.empty:
            x = x.reset_index()
            skrocony_terc = str(x.at[0, 'WOJ']).zfill(2) + str(int(float(str(x.at[0, 'POW'])))).zfill(2)
            return skrocony_terc

        else:
            x = tercbase.loc[(tercbase['NAZWA'] == name.upper()) & (tercbase['NAZWA_DOD'] == 'województwo')]

            if not x.empty:
                skrocony_terc = str(x.at[0, 'WOJ']).zfill(2)
                return skrocony_terc

            else:
                return False


# "Terencode" means "TERC-encode". This function
# searches captured gmina, powiat and voivoidship
# and returns its TERC codes.
# For example: "MAŁOPOLSKIE" returns 12.
def terencode(data):
    data = pd.DataFrame(data, index=[0])
    name = data.at[0, 'NAZWA']

    dname = name[::-1]
    dname = dname[::-1]

    if dname.find(" (") != -1:
        for i in dname:

            if i == '(':
                fromindex = dname.find(i) - 1
                dname = dname.replace(dname[fromindex::], '')
                data = data.replace(name, dname)

    dcols = data.columns.tolist()

    if dcols == ['NAZWA']:
        teryt = {'NAZWA': data.at[0, 'NAZWA']}
        teryt = pd.DataFrame(teryt, index=[0])
        return teryt

    # Capturing voivoidship's TERC ID.
    teryt = {'NAZWA': dname}  # {name: pagename}
    woj = data.at[0, 'województwo']
    wojewodztwa = tercbase.loc[(tercbase['NAZWA_DOD'] == 'województwo') & (tercbase['NAZWA'] == woj)]
    windex = wojewodztwa.index.tolist()
    teryt1 = {'WOJ': tercbase.at[windex[0], 'WOJ']}
    teryt.update(teryt1)
    cols = data.columns.tolist()

    # Cleaning powiat's name.
    if 'powiat' in cols:
        pot = data.at[0, 'powiat']
        if pot.find(" (") != -1:
            fromindex = ''
            for i in pot:

                if i == '(':
                    fromindex = pot.find(i) - 1

            # Deleting annotation, eg. '(województwo śląskie)'.
            pot = pot.replace(pot[fromindex::], '')

        # Adding powiat name.
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
                fromindex = ''
                for i in gmi:

                    if i == '(':
                        fromindex = gmi.find(i) - 1

                # Deleting annotation, eg. '(województwo śląskie)'.
                gmi = gmi.replace(gmi[fromindex::], '')
            gminy = tercbase.loc[
                ((tercbase['NAZWA_DOD'] == 'gmina miejska') |
                 (tercbase['NAZWA_DOD'] == 'obszar wiejski') |
                 (tercbase['NAZWA_DOD'] == 'gmina wiejska') |
                 (tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) &
                (tercbase['NAZWA'] == gmi) &
                (tercbase['POW'] == tercbase.at[pindex[0], 'POW'])]

            if gminy.empty:

                gminy = tercbase.loc[
                    ((tercbase['NAZWA_DOD'] == 'gmina miejska') |
                     (tercbase['NAZWA_DOD'] == 'obszar wiejski') |
                     (tercbase['NAZWA_DOD'] == 'gmina wiejska') |
                     (tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                            tercbase['NAZWA'] == gmi) & (
                            tercbase['POW'] == tercbase.at[windex[0], 'WOJ'])]

                if gminy.empty:
                    gminy = tercbase.loc[
                        ((tercbase['NAZWA_DOD'] == 'gmina miejska') |
                         (tercbase['NAZWA_DOD'] == 'obszar wiejski') |
                         (tercbase['NAZWA_DOD'] == 'gmina wiejska') |
                         (tercbase['NAZWA_DOD'] == 'gmina miejsko-wiejska')) &
                        (tercbase['NAZWA'] == gmi)]

            gindex = gminy.index.tolist()
            teryt3 = {'GMI': (tercbase.at[gindex[0], 'GMI'] + tercbase.at[gindex[0], 'RODZ'])}
            teryt.update(teryt3)

    teryt = pd.DataFrame(teryt, index=[0])

    # Done encoding!
    return teryt


# Function predestinated to capture SIMC IDs
# from the government's official database.
# For example, 'Strzebiń' returns 0135540.
# Data captured from terencode() are obviously
# required.
def filtersimc(data):
    tw = ''
    tp = ''
    tg = ''

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

    # Advanced filtering the SIMC database.
    # Capturing the data is maximally optimized
    # and based on reduction.
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

    # Despite that TERYT is already captured,
    # it doesn't need to be correct. To be sure of it,
    # TERYT will have to pass a 'verification'
    # of its correctness. If it's different than providen
    # at the beginning, that means some data need
    # to be actualised, doesn't it? ;)
    goal = goal[['NAZWA', 'WOJ', 'POW', 'GMI', 'RODZ_GMI', 'SYM']].reset_index()

    oldterc = [str(data.at[0, 'WOJ']).zfill(2) if 'WOJ' in data else str(goal.at[0, 'WOJ']).zfill(2),
               str(int(data.at[0, 'POW'])).zfill(2) if 'POW' in data else str(goal.at[0, 'POW']).zfill(2),
               str(int(data.at[0, 'GMI'])).zfill(3) if 'GMI' in data else str(str(goal.at[0, 'GMI']).zfill(2) +
                                                                              str(goal.at[0, 'RODZ_GMI']).zfill(1))]
    oldtercd = oldterc
    oldterc = oldterc[0] + oldterc[1] + oldterc[2]

    newtercd = {'województwo': str(goal.at[0, 'WOJ']).zfill(2), 'powiat': str(goal.at[0, 'POW']).zfill(2),
                'gmina': str(str(goal.at[0, 'GMI']).zfill(2) + str(goal.at[0, 'RODZ_GMI']).zfill(1))}
    newterc = newtercd['województwo'] + newtercd['powiat'] + newtercd['gmina']
    elements = ['województwo', 'powiat', 'gmina']

    apterc = ''

    if cp('cokolwiek', nazwa):
        apterc = cp('cokolwiek', nazwa)
        gapterc.append(apterc)

    globtercc.append(newterc)
    globterc.update(newtercd)

    geolocbot.output('(1.) TERC: ' + (apterc if not apterc == '' else newterc))

    if oldterc != newterc and len(newterc) == 7:
        for i in range(0, len(elements), 1):
            if oldtercd[i] != newtercd[elements[i]]:
                geolocbot.output("Zauważono potencjalną niepoprawność w kategoriach jednostek terytorialnych.")
                print(" " * 4 + 'W polu ' + elements[i] + ' prawdopodobnie są nieaktualne dane.')
                print(" " * 4 + 'Szczegóły błędu:')
                print(" " * 20 + 'Nasze:    ' + oldterc)
                print(" " * 20 + 'Aktualne: ' + newterc)
                site = pwbot.Site('pl', 'nonsensopedia')
                pg = pwbot.Page(site, u"Nonsensopedia:Lokalizacja/raporty")
                text = pg.text

                try:
                    if globname[0] not in text:
                        pg.text = text + '\n== [[' + globname[0] + \
                                  ']] ==\n\n<pre>* Pole:         ' + str(elements[i]) + \
                                  "\n* TERC lokalny: " + oldterc + '\n* TERC rządowy: ' + \
                                  newterc + '</pre>\n\n~~~~~\n----\n\n'
                        pg.save(u'/* raport */ ' + globname[0])

                except pwbot.exceptions.MaxlagTimeoutError:
                    if globname[0] not in text:
                        pg.text = text + '\n== [[' + globname[0] + \
                                  ']] ==\n\n<pre>* Pole:        ' + str(elements[i]) + \
                                  "\n* TERC lokalny: " + oldterc + '\n* TERC rządowy: ' + \
                                  newterc + '</pre>\n\n~~~~~\n----\n\n'
                        pg.save(u'/* raport */ ' + globname[0])

    # If the number of rows is bigger than 1,
    # the captured data isn't certain.
    if goal.shape[0] > 1:
        raise TooManyRows(goal[['NAZWA', 'SYM']])

    else:
        # (Expecting only one row, please look above).
        sym = goal.at[0, 'SYM']
        sym = str(sym).zfill(7)
        geolocbot.output('(::) SIMC: ' + sym)
        alldata = {'SIMC': sym, 'TERC': newterc}
        return alldata
