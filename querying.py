# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import pywikibot as pwbot
import pandas as pd
from __init__ import geolocbot
from databases import databasename, gapterc, globname, globterc, globtercc
from pywikibot import pagegenerators as pg

# Yet!
everythingiknow = {}


def cleanup_querying():
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if everythingiknow != {}:
        for key_value in list(everythingiknow.keys()):
            del everythingiknow[key_value]


class geolocbotQuery(object):
    def __init__(self):
        self.nts_database = pd.read_csv("NTS.csv", sep=';')
        self.terc_database = pd.read_csv("TERC.csv", sep=';',
                                         usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])
        self.uncertain = []
        self.item_get_attempts = []

    def ntsplease(self, mode='certain'):
        geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        if mode == 'certain':
            filtered_nts = self.nts_database.loc[self.nts_database['NAZWA'] == databasename[0]].reset_index()
            locnts = {}
            globnts = []

            for nts_index in range(filtered_nts.shape[0]):
                nts_id = ("{0}{1}{2}{3}{4}".format(str(int(filtered_nts.at[nts_index, 'REGION'])),
                                                   str(int(filtered_nts.at[nts_index, 'WOJ'])).zfill(2),
                                                   str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(2),
                                                   str(int(filtered_nts.at[nts_index, 'POW'])).zfill(2),
                                                   ((str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                                                     str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', '') if
                                                    pd.notna(filtered_nts.at[nts_index, 'GMI']) else '')))

                terc_odp = nts_id[1:3] + nts_id[5::]
                line = {terc_odp: nts_id}
                locnts.update(line)

            show = str(locnts).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')

            geolocbot.output(show)

            for i in range(len(locnts) - 1):

                if globtercc[0] != list(locnts.keys())[i]:
                    geolocbot.output('' + globtercc[0] + ' != ' + list(locnts.keys())[i] + ' – wartość usunięta.')
                    del locnts[list(locnts.keys())[i]]

            geolocbot.output('(1.) NTS:  ' + locnts[globtercc[0]])
            globnts.append(locnts[globtercc[0]])
            return globnts[0]

        elif mode == 'uncertain':
            filtered_nts = self.nts_database.loc[self.nts_database['NAZWA'] == globname[0]].reset_index()
            locnts = []

            for nts_index in range(filtered_nts.shape[0]):
                nts_id = (str(int(filtered_nts.at[nts_index, 'REGION'])) + str(
                    int(filtered_nts.at[nts_index, 'WOJ'])).zfill(
                    2) + str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(
                    2) + str(int(filtered_nts.at[nts_index, 'POW'])).zfill(
                    2) + (str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                          str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', ''))

                locnts.append(nts_id)

            geolocbot.output('Zwracam tablicę: ' + str(locnts).replace('[', '').replace(']', '') + '.')

            return locnts

    def terc_or_not(self, data):
        geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        shouldbeterc = self.terc_database.copy()
        shouldbeterc = shouldbeterc.loc[(shouldbeterc['NAZWA'] == databasename[0])]
        sterc = shouldbeterc.copy()

        if sterc.empty:
            geolocbot.output("" + globname[0] + " nie występuje w systemie TERC. Usuwam klucz…")
            del data['terc']
            return data

        shouldbeterc = sterc.loc[
            (sterc['WOJ'] == float(globterc['województwo'])) & (sterc['POW'] == float(globterc['powiat'])) &
            (sterc['GMI'] == float(globterc['gmina']))]

        if shouldbeterc.empty:
            shouldbeterc = shouldbeterc.loc[
                (shouldbeterc['WOJ'] == float(globterc['województwo'])) &
                (shouldbeterc['POW'] == float(int(globterc['powiat'])))]

            if shouldbeterc.empty:
                tercb = self.terc_database.loc[
                    (self.terc_database['WOJ'] == float(globterc['województwo']))]

                if tercb.empty:
                    geolocbot.output("Miejscowość " + globname[0] +
                                     " nie spełnia kryteriów TERC, więc identyfikator nie zostanie"
                                     " dołączony do szablonu."
                                     " Usuwam klucz…")
                    del data['terc']
                    return data

        geolocbot.output(
            'Miejscowość ' + globname[0] + ' spełnia kryteria TERC, więc identyfikator zostanie dołączony' +
            ' do szablonu.')

        if gapterc:
            del data['terc']
            nterc = {'terc': gapterc[0]}
            data.update(nterc)

        return data

    @staticmethod
    def get_Q_id(data):
        geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        sid = data['SIMC']

        # Please don't confuse with 'Lidl'. :D
        sidl = {'simc': sid}
        everythingiknow.update(sidl)

        terid = data['TERC']
        tidl = {'terc': terid}
        everythingiknow.update(tidl)

        query = """SELECT ?coord ?item ?itemLabel 
        WHERE
        {
          ?item wdt:P4046 '""" + sid + """'.
          OPTIONAL {?item wdt:P625 ?coord}.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
        }"""

        wikidata_site = pwbot.Site("wikidata", "wikidata")
        generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
        x = list(generator)

        if not x:

            query = """SELECT ?coord ?item ?itemLabel 
                WHERE
                {
                  ?item wdt:P1653 '""" + terid + """'.
                  OPTIONAL {?item wdt:P625 ?coord}.
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                }"""

            generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
            x = list(generator)

            if not x:
                try:
                    geolocbot.output('Ustawiono tryb domyślny NTS.')

                    query = """SELECT ?coord ?item ?itemLabel 
                        WHERE
                        {
                          ?item wdt:P1653 '""" + geolocbotQuery.ntsplease() + """'.
                          OPTIONAL {?item wdt:P625 ?coord}.
                          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                        }"""

                    generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                    x = list(generator)

                except KeyError:
                    geolocbot.output('Domyślny tryb NTS nie zwrócił wyniku.')
                    geolocbot.output('Ustawiono niepewny tryb NTS.')

                    ntr = geolocbotQuery.ntsplease(mode='uncertain')
                    for i in range(len(ntr)):

                        query = """SELECT ?coord ?item ?itemLabel 
                            WHERE
                            {
                              ?item wdt:P1653 '""" + ntr[i] + """'.
                              OPTIONAL {?item wdt:P625 ?coord}.
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                            }"""

                        generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                        x = list(generator)

                        if x:
                            change_mode(1)
                            break

                if not x:
                    raise KeyError('Niczego nie znalazłem w Wikidata. [b]')

        string = ''.join(map(str, x))
        qidentificator = string.replace("[[wikidata:", "").replace("]]", "")
        qidl = {'wikidata': qidentificator}
        everythingiknow.update(qidl)
        geolocbot.output('(::) QID:  ' + str(qidentificator))
        return qidentificator

    def get_item_info(self, item):
        geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        try:
            item.get()

        except pwbot.exceptions.MaxlagTimeoutError:
            self.item_get_attempts.append(1)
            attempt = len(self.item_get_attempts)
            geolocbot.output(f'Timeout. Próbuję jeszcze raz, próba: {attempt}.')
            geolocbotQuery.get_item_info(item)


site = pwbot.Site("wikidata", "wikidata")
repo = site.data_repository()


def coords(qid):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    item = pwbot.ItemPage(repo, qid)

    geolocbotQuery.get_item_info(item)

    if item.claims:
        item = pwbot.ItemPage(repo, qid)  # This will be functionally the same as the other item we defined
        wikidata_data = item.get()
        attempts = []

        for i in range(len(list(wikidata_data['labels']))):
            if databasename[0] == wikidata_data['labels'][list(wikidata_data['labels'])[i]]:
                geolocbot.output('Nazwy są jednakowe (wynik próby ' + str(len(attempts) + 1) + ').')
                break

            else:
                attempts.append(i)

        if len(attempts) == len(list(wikidata_data['labels'])):
            raise KeyError(
                'Na Wikidata są koordynaty miejscowości o tym samym identyfikatorze, jednak nie o tej samej nazwie. '
                'Liczba prób porównawczych: ' + str(len(attempts) + 1) + '.')

        if 'P625' in item.claims:
            coordinates = item.claims['P625'][0].getTarget()
            latitude = coordinates.lat
            longitude = coordinates.lon
            coordins = {'koordynaty': str(latitude)[:10] + ', ' + str(longitude)[:10]}
            everythingiknow.update(coordins)

    return geolocbotQuery.terc_or_not(everythingiknow)  # ;)


def change_mode(integer=None):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if geolocbotQuery.uncertain != [] or integer is None:
        for i in range(len(geolocbotQuery.uncertain)):
            del geolocbotQuery.uncertain[i]

    else:
        geolocbotQuery.uncertain.append(integer)
