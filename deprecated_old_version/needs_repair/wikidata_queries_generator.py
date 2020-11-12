# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import pywikibot as pwbot
import pandas as pd
from __init__ import geolocbotMain
from databases_search_engine import geolocbotDatabases
from pywikibot import pagegenerators


class geolocbotQuery(object):
    def __init__(self):
        self.nts_database = pd.read_csv("NTS.csv", sep=';')
        self.terc_database = pd.read_csv("TERC.csv", sep=';',
                                         usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])
        self.uncertain = []
        self.item_get_attempts = []
        self.wikidata = pwbot.Site("wikidata", "wikidata")
        self.repo = self.wikidata.data_repository()
        self.searched_data = {}

    def cleanup_queries_generator(self):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        if self.searched_data != {}:
            for key_value in list(self.searched_data.keys()):
                del self.searched_data[key_value]

    def generate_nts_identificator(self, mode='certain'):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        if mode == 'certain':
            filtered_nts = self.nts_database.loc[self.nts_database['NAZWA'] ==
                                                 geolocbotDatabases.main_name_for_databases[0]].reset_index()
            nts_codes_to_compare = {}
            final_nts_code = []

            for nts_index in range(filtered_nts.shape[0]):
                nts_id = ("{0}{1}{2}{3}{4}".format(str(int(filtered_nts.at[nts_index, 'REGION'])),
                                                   str(int(filtered_nts.at[nts_index, 'WOJ'])).zfill(2),
                                                   str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(2),
                                                   str(int(filtered_nts.at[nts_index, 'POW'])).zfill(2),
                                                   ((str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                                                     str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', '') if
                                                    pd.notna(filtered_nts.at[nts_index, 'GMI']) else '')))

                terc_code_equivalent = nts_id[1:3] + nts_id[5::]
                line = {terc_code_equivalent: nts_id}
                nts_codes_to_compare.update(line)

            show = str(nts_codes_to_compare).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')

            geolocbotMain.debug.output(show)

            for i in range(len(nts_codes_to_compare) - 1):

                if geolocbotDatabases.main_terc_id_code[0] != list(nts_codes_to_compare.keys())[i]:
                    geolocbotMain.debug.output('' + geolocbotDatabases.main_terc_id_code[0] + ' != ' +
                                               list(nts_codes_to_compare.keys())[i] + ' – wartość usunięta.')
                    del nts_codes_to_compare[list(nts_codes_to_compare.keys())[i]]

            geolocbotMain.output('(1.) NTS:  ' + nts_codes_to_compare[geolocbotDatabases.main_terc_id_code[0]])
            final_nts_code.append(nts_codes_to_compare[geolocbotDatabases.main_terc_id_code[0]])
            return final_nts_code[0]

        elif mode == 'uncertain':
            filtered_nts = self.nts_database.loc[
                self.nts_database['NAZWA'] == geolocbotDatabases.main_name[0]].reset_index()
            nts_codes_to_compare = []

            for nts_index in range(filtered_nts.shape[0]):
                nts_id = (str(int(filtered_nts.at[nts_index, 'REGION'])) + str(
                    int(filtered_nts.at[nts_index, 'WOJ'])).zfill(
                    2) + str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(
                    2) + str(int(filtered_nts.at[nts_index, 'POW'])).zfill(
                    2) + (str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                          str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', ''))

                nts_codes_to_compare.append(nts_id)

            geolocbotMain.debug.output('Zwracam tablicę: ' + str(nts_codes_to_compare).replace('[', '').replace(']', '')
                                       + '.')

            return nts_codes_to_compare

    def terc_or_not(self, data):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        terc_database_copy_1 = self.terc_database.copy()
        terc_database_copy_1 = terc_database_copy_1.loc[(terc_database_copy_1['NAZWA'] ==
                                                         geolocbotDatabases.main_name_for_databases[0])]
        terc_database_copy_2 = terc_database_copy_1.copy()

        if terc_database_copy_2.empty:
            geolocbotMain.output("" + geolocbotDatabases.main_name[0] + " nie występuje w systemie TERC. Usuwam klucz…")
            del data['terc']
            return data

        terc_database_copy_1 = terc_database_copy_2.loc[
            (terc_database_copy_2['WOJ'] == float(geolocbotDatabases.main_terc_id_info['województwo'])) & (
                    terc_database_copy_2['POW'] == float(geolocbotDatabases.main_terc_id_info['powiat'])) &
            (terc_database_copy_2['GMI'] == float(geolocbotDatabases.main_terc_id_info['gmina']))]

        if terc_database_copy_1.empty:
            terc_database_copy_1 = terc_database_copy_1.loc[
                (terc_database_copy_1['WOJ'] == float(geolocbotDatabases.main_terc_id_info['województwo'])) &
                (terc_database_copy_1['POW'] == float(int(geolocbotDatabases.main_terc_id_info['powiat'])))]

            if terc_database_copy_1.empty:
                terc_database_copy_3 = self.terc_database.loc[
                    (self.terc_database['WOJ'] == float(geolocbotDatabases.main_terc_id_info['województwo']))]

                if terc_database_copy_3.empty:
                    geolocbotMain.output("Miejscowość " + geolocbotDatabases.main_name[0] +
                                         " nie spełnia kryteriów TERC, więc identyfikator nie zostanie"
                                         " dołączony do szablonu."
                                         " Usuwam klucz…")
                    del data['terc']
                    return data

        geolocbotMain.output(
            f'Miejscowość {geolocbotDatabases.main_name[0]} spełnia kryteria TERC, więc identyfikator zostanie '
            f'dołączony do szablonu.')

        if geolocbotDatabases.main_terc_id_shortened:
            del data['terc']
            terc_id_shortened = {'terc': geolocbotDatabases.main_terc_id_shortened[0]}
            data.update(terc_id_shortened)

        return data

    def SPARQL(self, data):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        simc_id_to_ask = data['SIMC']

        # Please don't confuse with 'Lidl'. :D
        simc_id_in_dict = {'simc': simc_id_to_ask}
        self.searched_data.update(simc_id_in_dict)

        terc_id_to_ask = data['TERC']
        terc_id_in_dict = {'terc': terc_id_to_ask}
        self.searched_data.update(terc_id_in_dict)

        query = """SELECT ?coord ?item ?itemLabel 
        WHERE
        {
          ?item wdt:P4046 '""" + simc_id_to_ask + """'.
          OPTIONAL {?item wdt:P625 ?coord}.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
        }"""

        wikidata_site = pwbot.Site("wikidata", "wikidata")
        sparql_query_result = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
        wikidata_id = list(sparql_query_result)

        if not wikidata_id:

            query = """SELECT ?coord ?item ?itemLabel 
                WHERE
                {
                  ?item wdt:P1653 '""" + terc_id_to_ask + """'.
                  OPTIONAL {?item wdt:P625 ?coord}.
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                }"""

            sparql_query_result = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
            wikidata_id = list(sparql_query_result)

            if not wikidata_id:
                try:
                    geolocbotMain.debug.output('Ustawiono tryb domyślny NTS.')

                    query = """SELECT ?coord ?item ?itemLabel 
                        WHERE
                        {
                          ?item wdt:P1653 '""" + geolocbotQuery.generate_nts_identificator() + """'.
                          OPTIONAL {?item wdt:P625 ?coord}.
                          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                        }"""

                    sparql_query_result = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                    wikidata_id = list(sparql_query_result)

                except KeyError:
                    geolocbotMain.debug.output('Domyślny tryb NTS nie zwrócił wyniku.')
                    geolocbotMain.debug.output('Ustawiono niepewny tryb NTS.')

                    one_of_a_few_nts_ids = geolocbotQuery.generate_nts_identificator(mode='uncertain')
                    for index in range(len(one_of_a_few_nts_ids)):

                        query = """SELECT ?coord ?item ?itemLabel 
                            WHERE
                            {
                              ?item wdt:P1653 '""" + one_of_a_few_nts_ids[index] + """'.
                              OPTIONAL {?item wdt:P625 ?coord}.
                              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                            }"""

                        sparql_query_result = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                        wikidata_id = list(sparql_query_result)

                        if wikidata_id:
                            geolocbotQuery.change_mode(1)
                            break

                if not wikidata_id:
                    raise ValueError('Nie odnaleziono spełniającego objęte kryteria elementu w Wikidata.')

        wikidata_id_in_string = ''.join(map(str, wikidata_id))
        wikidata_searched_id = wikidata_id_in_string.replace('[[wikidata:', '').replace(']]', '')
        wikidata_searched_id_in_dict = {'wikidata': wikidata_searched_id}
        self.searched_data.update(wikidata_searched_id_in_dict)
        geolocbotMain.output('(::) QID:  ' + str(wikidata_searched_id))
        return wikidata_searched_id

    def get_item_info(self, wikidata_id_of_item):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        try:
            wikidata_id_of_item.get()

        except pwbot.exceptions.MaxlagTimeoutError:
            self.item_get_attempts.append(1)
            attempt = len(self.item_get_attempts)
            geolocbotMain.output(f'Timeout. Ponawiam zapytanie {attempt} raz.')
            geolocbotQuery.get_item_info(wikidata_id_of_item)

    def collect_geocoordinates(self, wikidata_id_of_item):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        item = pwbot.ItemPage(self.repo, wikidata_id_of_item)

        geolocbotQuery.get_item_info(item)

        if item.claims:
            item = pwbot.ItemPage(self.repo, wikidata_id_of_item)
            wikidata_data = item.get()
            attempts = []

            for i in range(len(list(wikidata_data['labels']))):
                if geolocbotDatabases.main_name_for_databases[0] == \
                        wikidata_data['labels'][list(wikidata_data['labels'])[i]]:
                    geolocbotMain.output('Nazwy są jednakowe (wynik próby ' + str(len(attempts) + 1) + ').')
                    break

                else:
                    attempts.append(i)

            if len(attempts) == len(list(wikidata_data['labels'])):
                raise KeyError(
                    'Na Wikidata są koordynaty miejscowości o tym samym identyfikatorze, '
                    'jednak nie o tej samej nazwie. '
                    'Liczba prób porównawczych: ' + str(len(attempts) + 1) + '.')

            if 'P625' in item.claims:
                coordinates = item.claims['P625'][0].getTarget()
                latitude = coordinates.lat
                longitude = coordinates.lon
                coordinates = {'koordynaty': str(latitude)[:10] + ', ' + str(longitude)[:10]}
                self.searched_data.update(coordinates)

        return geolocbotQuery.terc_or_not(self.searched_data)

    @staticmethod
    def change_mode(integer=None):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        if geolocbotQuery.uncertain != [] or integer is None:
            for i in range(len(geolocbotQuery.uncertain)):
                del geolocbotQuery.uncertain[i]

        else:
            geolocbotQuery.uncertain.append(integer)


geolocbotQuery = geolocbotQuery()
