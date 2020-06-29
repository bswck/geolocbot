# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
# This is a cool tool for returning TERYT codes of provinces etc.
# Read more: http://eteryt.stat.gov.pl/eTeryt/english.aspx?contrast=default.
import inspect
import types
from typing import cast
import pywikibot as pwbot
import pandas as pd
from __init__ import geolocbot

simc_database = pd.read_csv("SIMC.csv", sep=';',
                            usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM'])
terc_database = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])

globname = []
globterc = {}
globtercc = []
gapterc = []
databasename = []


def cleanup_databases(exclude=None):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if exclude is None:
        exclude = ['']

    if 'globname' not in exclude:
        while globname:
            del globname[0]

    if 'globterc' not in exclude:
        if globterc != {}:
            for key_value in list(globterc.keys()):
                del globterc[key_value]

    if 'globtercc' not in exclude:
        while globtercc:
            del globtercc[0]

    if 'gapterc' not in exclude:
        while gapterc:
            del gapterc[0]

    if 'databasename' not in exclude:
        while databasename:
            del databasename[0]


def updatename(name):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if len(globname) >= 1:
        del globname[0]

    globname.append(name)
    geolocbot.output('Adres docelowy to [[' + name + ']].')


def check_status(typ, name):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if typ == 'gmina':
        gmina = terc_database.loc[(terc_database['NAZWA'] == name) &
                                  ((terc_database['NAZWA_DOD'] == 'gmina miejska') |
                                   (terc_database['NAZWA_DOD'] == 'obszar wiejski') |
                                   (terc_database['NAZWA_DOD'] == 'gmina wiejska') |
                                   (terc_database['NAZWA_DOD'] == 'gmina miejsko-wiejska'))]

        if gmina.empty:
            return False

        else:
            gmina = gmina.reset_index()
            return gmina.at[0, 'NAZWA']

    elif typ == 'powiat':
        powiat = terc_database.loc[(terc_database['NAZWA'] == name) & (
                (terc_database['NAZWA_DOD'] == typ) | (terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

        if powiat.empty:
            return False

        else:
            powiat = powiat.reset_index()
            return powiat.at[0, 'NAZWA']

    else:
        target = terc_database.loc[(terc_database['NAZWA'] == name) & (
                (terc_database['NAZWA_DOD'] == 'powiat') | (terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

        if not target.empty:
            target = target.reset_index()
            terc_id_shortened = str(target.at[0, 'WOJ']).zfill(2) + str(int(float(str(target.at[0, 'POW'])))).zfill(2)
            return terc_id_shortened

        else:
            target = terc_database.loc[(terc_database['NAZWA'] == name.upper()) &
                                       (terc_database['NAZWA_DOD'] == 'województwo')]

            if not target.empty:
                terc_id_shortened = str(target.at[0, 'WOJ']).zfill(2)
                return terc_id_shortened

            else:
                return False


# "Terencode" means "TERC-encode". This function
# searches captured gmina, powiat and voivoidship
# and returns its TERC codes.
# For example: "MAŁOPOLSKIE" returns 12.
def encode_to_terc(data):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    data = pd.DataFrame(data, index=[0])
    name = data.at[0, 'NAZWA']

    dname = name[::-1]
    dname = dname[::-1]

    if dname.find(" (") != -1:
        for i in dname:

            if i == '(':
                fromindex = dname.find(i) - 1
                dname = dname.replace(dname[fromindex::], '')
                geolocbot.output("Usunięto z podanej nazwy dopisek '" + name[fromindex + 1::] + "' na potrzeby"
                                                                                                " baz danych.")
                data = data.replace(name, dname)

    databasename.append(dname)
    geolocbot.output('Nazwa wykorzystywana w przeszukiwaniu baz danych: ' + databasename[0] + '.')
    dcols = data.columns.tolist()

    if dcols == ['NAZWA']:
        teryt = {'NAZWA': data.at[0, 'NAZWA']}
        teryt = pd.DataFrame(teryt, index=[0])
        return teryt

    # Capturing voivoidship's TERC ID.
    teryt = {'NAZWA': dname}  # {name: pagename}
    woj = data.at[0, 'województwo']
    wojewodztwa = terc_database.loc[(terc_database['NAZWA_DOD'] == 'województwo') & (terc_database['NAZWA'] == woj)]
    windex = wojewodztwa.index.tolist()
    teryt1 = {'WOJ': terc_database.at[windex[0], 'WOJ']}
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
        powiaty = terc_database.loc[((terc_database['NAZWA_DOD'] == 'powiat') |
                                     (terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu')) &
                                    (terc_database['NAZWA'] == pot) &
                                    (terc_database['WOJ'] == terc_database.at[windex[0], 'WOJ'])]

        if powiaty.empty:
            powiaty = terc_database.loc[
                (((terc_database['NAZWA_DOD'] == 'powiat') |
                  (terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu')) &
                 (terc_database['NAZWA'] == pot))]

        pindex = powiaty.index.tolist()
        teryt2 = {'POW': int(terc_database.at[pindex[0], 'POW'])}
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
            gminy = terc_database.loc[
                ((terc_database['NAZWA_DOD'] == 'miasto') |
                 (terc_database['NAZWA_DOD'] == 'gmina miejska') |
                 (terc_database['NAZWA_DOD'] == 'obszar wiejski') |
                 (terc_database['NAZWA_DOD'] == 'gmina wiejska') |
                 (terc_database['NAZWA_DOD'] == 'gmina miejsko-wiejska')) &
                (terc_database['NAZWA'] == gmi) &
                (terc_database['POW'] == terc_database.at[pindex[0], 'POW'])]

            if gminy.empty:

                gminy = terc_database.loc[
                    ((terc_database['NAZWA_DOD'] == 'miasto') |
                     (terc_database['NAZWA_DOD'] == 'gmina miejska') |
                     (terc_database['NAZWA_DOD'] == 'obszar wiejski') |
                     (terc_database['NAZWA_DOD'] == 'gmina wiejska') |
                     (terc_database['NAZWA_DOD'] == 'gmina miejsko-wiejska')) & (
                            terc_database['NAZWA'] == gmi) & (
                            terc_database['POW'] == terc_database.at[pindex[0], 'WOJ'])]

                if gminy.empty:
                    gminy = terc_database.loc[
                        ((terc_database['NAZWA_DOD'] == 'miasto') |
                         (terc_database['NAZWA_DOD'] == 'gmina miejska') |
                         (terc_database['NAZWA_DOD'] == 'obszar wiejski') |
                         (terc_database['NAZWA_DOD'] == 'gmina wiejska') |
                         (terc_database['NAZWA_DOD'] == 'gmina miejsko-wiejska')) &
                        (terc_database['NAZWA'] == gmi)]

            gindex = gminy.index.tolist()

            teryt3 = {'GMI': str(int(terc_database.at[gindex[0], 'GMI'])) + str(
                int(terc_database.at[gindex[0], 'RODZ']))}

            teryt.update(teryt3)

    teryt = pd.DataFrame(teryt, index=[0])

    # Done encoding!
    return teryt


def simc_database_search(data):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    tw = ''
    tp = ''
    tg = ''
    ts = ''
    trg = ''

    elements = []

    if 'WOJ' in data:
        tw = int(data.at[0, 'WOJ'])
        elements.append('województwo')

    if 'POW' in data:
        tp = int(data.at[0, 'POW'])
        elements.append('powiat')

    if 'GMI' in data:
        twg = str(data.at[0, 'GMI'])[0]
        trg = int(str(data.at[0, 'GMI'])[1])
        tg = int(twg)
        elements.append('gmina i rodzaj gminy')

    if 'SIMC' in data:
        ts = int(data.at[0, 'SIMC'])
        elements.append('simc')

    nazwa = databasename[0]

    goal = simc_database.copy()

    if 'simc' in elements:
        goal = simc_database.loc[(simc_database['SYM'] == ts)]

    elif elements == ['województwo', 'powiat', 'gmina i rodzaj gminy']:
        goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                                 (simc_database['POW'] == tp) & (simc_database['GMI'] == tg) &
                                 (simc_database['GMI'] == trg)]

        if goal.empty:
            goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                                     (simc_database['POW'] == tp) & (simc_database['GMI'] == tg)]

            if goal.empty:
                goal = simc_database.loc[
                    (simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                    (simc_database['POW'] == tp)]

                if goal.empty:
                    goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) &
                                             (simc_database['WOJ'] == tw)]

    elif elements == ['województwo', 'powiat']:
        goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                                 (simc_database['POW'] == tp)]

        if goal.empty:
            goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw)]

    elif elements == ['województwo', 'gmina i rodzaj gminy']:
        goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                                 (simc_database['GMI'] == tg) &
                                 (simc_database['GMI'] == trg)]

        if goal.empty:
            goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw) &
                                     (simc_database['GMI'] == tg)]

            if goal.empty:
                goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw)]

    elif elements == ['województwo']:
        goal = simc_database.loc[(simc_database['NAZWA'] == nazwa) & (simc_database['WOJ'] == tw)]

    elif not elements:
        goal = simc_database.loc[(simc_database['NAZWA'] == nazwa)]

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
    elements = ['województwo', 'powiat']

    apterc = ''

    if check_status('nonsa wymiata', nazwa):  # this is an easter-egg
        apterc = check_status('rzer', nazwa)
        gapterc.append(apterc)

    globtercc.append(newterc)
    globterc.update(newtercd)

    geolocbot.output('(1.) TERC: ' + (apterc if apterc != '' else newterc))

    site = geolocbot.site

    if oldterc[:5] != newterc[:5] and len(newterc) == 7:
        for i in range(0, len(elements), 1):
            if oldtercd[i] != newtercd[elements[i]]:
                geolocbot.output("Zauważono potencjalną niepoprawność w kategoriach jednostek terytorialnych.")
                print(" " * 4 + 'W polu ' + elements[i] + ' prawdopodobnie są nieaktualne dane.')
                print(" " * 4 + 'Szczegóły błędu:')
                print(" " * 20 + 'Nasze:    ' + oldterc)
                print(" " * 20 + 'Aktualne: ' + newterc)
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

    hints_page = pwbot.Page(site, 'Dyskusja użytkownika:Stim/TooManyRows-hints')
    hints = hints_page.text

    if goal.shape[0] > 1 and globname[0] not in hints:
        geolocbot.too_many_rows_del()
        geolocbot.too_many_rows_in(dataframe=goal[['NAZWA', 'SYM']])
        raise geolocbot.exceptions.TooManyRows(goal[['NAZWA', 'SYM']])

    elif goal.shape[0] > 1 and globname[0] in hints:
        line_start = hints[(hints.find('| [[' + globname[0] + ']] || '))::]
        line = line_start[:(line_start.find('\n|-'))]
        simc_hint = line[(line.find('|| ') + 3)::]
        geolocbot.output('(nonsa.pl) [TooManyRows]: Pobrano wskazówkę SIMC: ' + str(simc_hint).zfill(7))
        return tmr_supported(simc_hint)

    sym = goal.at[0, 'SYM']
    sym = str(sym).zfill(7)
    geolocbot.output('(::) SIMC: ' + sym)
    alldata = {'SIMC': sym, 'TERC': newterc}
    return alldata


def tmr_supported(data):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    dataframe = simc_database.loc[simc_database['SYM'] == int(data)].reset_index()
    cleanup_databases(exclude=['globname', 'databasename'])
    line = {'WOJ': dataframe.at[0, 'WOJ'],
            'POW': dataframe.at[0, 'POW']}

    if pd.notna(dataframe.at[0, 'GMI']):
        gmiadd = {'GMI': int(str(dataframe.at[0, 'GMI']) + str(dataframe.at[0, 'RODZ_GMI']))}
        line.update(gmiadd)

    globterc.update(line)
    newtercc = "{0}{1}{2}".format(str(line['WOJ']).zfill(2), str(line['POW']).zfill(2),
                                  (str(line['GMI']).zfill(3) if 'GMI' in list(line.keys()) else ''))
    globtercc.append(newtercc)
    for_df = {'SIMC': [dataframe.at[0, 'SYM']],
              'WOJ': [dataframe.at[0, 'WOJ']],
              'POW': [dataframe.at[0, 'POW']]}

    if pd.notna(dataframe.at[0, 'GMI']):
        gmiadd = {'GMI': [int(str(dataframe.at[0, 'GMI']) + str(dataframe.at[0, 'RODZ_GMI']))]}
        for_df.update(gmiadd)

    newdata = pd.DataFrame.from_dict(for_df)
    print(newdata)
    return simc_database_search(newdata)
