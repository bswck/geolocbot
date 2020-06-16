# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
# This is a cool tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default.

import pywikibot as pwbot
import pandas as pd
import sys


class Error(Exception):
    """Base class for other exceptions"""
    pass


class TooManyRows(Error):
    """Raised when too many rows appear in the table as an answer"""
    pass


nts = pd.read_csv("NTS.csv", sep=';')
simc = pd.read_csv("SIMC.csv", sep=';',
                   usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM'])
tercbase = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])

globnts = []
globname = []
globterc = {}


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


# "Terencode" means "TERYT-encode". This function
# searches captured gmina, powiat and voivoidship
# and returns its TERYT codes.
# For example: "MAŁOPOLSKIE" returns 12.
def terencode(data):
    data = pd.DataFrame(data, index=[0])
    name = data.at[0, 'NAZWA']
    globname.append(name)

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

    # Capturing voivoidship's TERYT ID.
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

    oldterc = [str(data.at[0, 'WOJ']).zfill(2) if 'WOJ' in data else str(goal.at[0, 'WOJ']).zfill(2), str(int(data.at[0, 'POW'])).zfill(2) if 'POW' in data else str(goal.at[0, 'POW']).zfill(2), str(int(data.at[0, 'GMI'])).zfill(3) if 'GMI' in data else str(str(goal.at[0, 'GMI']).zfill(2) + str(goal.at[0, 'RODZ_GMI']).zfill(1))]
    oldtercd = oldterc
    oldterc = oldterc[0] + oldterc[1] + oldterc[2]
    newterc = str(goal.at[0, 'WOJ']).zfill(2) + str(goal.at[0, 'POW']).zfill(2) + str(str(goal.at[0, 'GMI']).zfill(2) + str(goal.at[0, 'RODZ_GMI']).zfill(1))
    newtercd = {'województwo': str(goal.at[0, 'WOJ']).zfill(2), 'powiat': str(goal.at[0, 'POW']).zfill(2), 'gmina': str(str(goal.at[0, 'GMI']).zfill(2) + str(goal.at[0, 'RODZ_GMI']).zfill(1))}
    globterc.update(newtercd)
    filtered_nts = nts.loc[nts['NAZWA'] == globname[0]].reset_index()
    locnts = {}

    for nts_index in range(filtered_nts.shape[0]):
        nts_id = (str(int(filtered_nts.at[nts_index, 'REGION'])) + str(int(filtered_nts.at[nts_index, 'WOJ'])).zfill(
            2) + str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(
            2) + str(int(filtered_nts.at[nts_index, 'POW'])) + str(
            int(filtered_nts.at[nts_index, 'GMI'])) + str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', '')
        terc_odp = nts_id[1:3] + nts_id[5::]
        line = {terc_odp: nts_id}
        locnts.update(line)

    print('[b] ' + str(locnts))

    for i in range(len(locnts) - 1):

        if newterc != list(locnts.keys())[i]:
            print('[b] ' + newterc + ' != ' + list(locnts.keys())[i] + ' – wartość usunięta.')
            del locnts[list(locnts.keys())[i]]

    print('[b] (1.) NTS:  ' + locnts[newterc])
    globnts.append(locnts[newterc])

    elements = ['województwo', 'powiat', 'gmina']
    print('[b] (1.) TERC: ' + newterc)

    if oldterc != newterc:
        for i in range(0, len(elements), 1):
            if oldtercd[i] != newtercd[elements[i]]:
                print("[b] Sugeruję uaktualnienie danych, Anżej,")
                print(" " * 4 + 'bo w polu ' + elements[i] + ' są nieaktualne dane.')
                print(" " * 4 + 'Porównaj:')
                print()
                print(" " * 4 + 'Nasze:    ' + oldterc)
                print(" " * 4 + 'Aktualne: ' + newterc)
                site = pwbot.Site('pl', 'nonsensopedia')
                pg = pwbot.Page(site, u"Dyskusja użytkownika:Stim")
                text = pg.text

                try:
                    if globname[0] not in text:
                        pg.text = text + '\n== Zgłoszenie nieprawidłowego TERC pochodzącego z [[' + globname[0] + ']] ==\n\nW artykule [[' + globname[0] + ']] mogą być nieaktualne kategorie jednostek administracyjnych. Nieprawidłowość wykryto w polu ' + str(elements[i]) + '.\n\nSzczegóły błędu:\n# Nasz TERC: ' + oldterc + ';\n# Rządowy TERC: ' + newterc + '.\n\n[[Użytkownik:StimBOT|StimBOT]] ~~~~~'
                        pg.save(u'Zgłaszam nieprawidłowy TERC')

                except pwbot.exceptions.MaxlagTimeoutError:
                    if globname[0] not in text:
                        pg.text = text + '\n== Zgłoszenie nieprawidłowego TERC pochodzącego z [[' + globname[0] + ']] ==\n\nW artykule [[' + globname[0] + ']] mogą być nieaktualne kategorie jednostek administracyjnych. Nieprawidłowość wykryto w polu ' + str(elements[i]) + '.\n\nSzczegóły błędu:\n# Nasz TERC: ' + oldterc + ';\n# Rządowy TERC: ' + newterc + '.\n\n[[Użytkownik:StimBOT|StimBOT]] ~~~~~'
                        pg.save(u'Zgłaszam nieprawidłowy TERC')

    # If the number of rows is bigger than 1,
    # it means the captured data isn't certain.
    if goal.shape[0] > 1:
        raise TooManyRows(goal[['NAZWA', 'SYM']])

    else:
        # (Expecting only one row, please look above).
        sym = goal.at[0, 'SYM']
        sym = str(sym).zfill(7)
        print('[b] (::) SIMC: ' + sym)
        alldata = {'SIMC': sym, 'TERC': newterc}
        return alldata
