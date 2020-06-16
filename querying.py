# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import pywikibot as pwbot
import pandas as pd
from databases import globname, globterc, globtercc, updatename
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator
from pywikibot.bot import SingleSiteBot
from pywikibot import pagegenerators as pg
from coordinates import Coordinate

# Yet!
everythingiknow = {}

nts = pd.read_csv("NTS.csv", sep=';')
tercbase = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])
uncertain = []


def changemode(integer=None):
    if uncertain != []:
        for i in range(len(uncertain)):
            del uncertain[i]

    if integer is None:
        for i in range(len(uncertain)):
            del uncertain[i]

    else:
        uncertain.append(integer)


def ntsplease(mode='certain'):
    if mode == 'certain':
        filtered_nts = nts.loc[nts['NAZWA'] == globname[0]].reset_index()
        locnts = {}
        globnts = []

        for nts_index in range(filtered_nts.shape[0]):
            nts_id = (str(int(filtered_nts.at[nts_index, 'REGION'])) +
                      str(int(filtered_nts.at[nts_index, 'WOJ'])).zfill(2) +
                      str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(2) +
                      str(int(filtered_nts.at[nts_index, 'POW'])).zfill(2) +
                      (str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                       str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', ''))

            terc_odp = nts_id[1:3] + nts_id[5::]
            line = {terc_odp: nts_id}
            locnts.update(line)

        print('[b] ' + str(locnts))

        for i in range(len(locnts) - 1):

            if globtercc[0] != list(locnts.keys())[i]:
                print('[b] ' + globtercc[0] + ' != ' + list(locnts.keys())[i] + ' – wartość usunięta.')
                del locnts[list(locnts.keys())[i]]

        print('[b] (1.) NTS:  ' + locnts[globtercc[0]])
        globnts.append(locnts[globtercc[0]])
        return globnts[0]

    elif mode == 'uncertain':
        print('[b] Tryb domyślny (NTS) nie zwrócił wyniku.')
        print('[b] Podejmuję próbę w trybie niepewnym (NTS)…')
        filtered_nts = nts.loc[nts['NAZWA'] == globname[0]].reset_index()
        locnts = []

        for nts_index in range(filtered_nts.shape[0]):
            nts_id = (str(int(filtered_nts.at[nts_index, 'REGION'])) + str(
                int(filtered_nts.at[nts_index, 'WOJ'])).zfill(
                2) + str(int(filtered_nts.at[nts_index, 'PODREG'])).zfill(
                2) + str(int(filtered_nts.at[nts_index, 'POW'])).zfill(
                2) + (str(int(filtered_nts.at[nts_index, 'GMI'])).zfill(2) +
                      str(int(filtered_nts.at[nts_index, 'RODZ']))).replace('.', ''))

            print('[b] ' + str(nts_id))
            locnts.append(nts_id)

        print('[b] Zwracam tablicę: ' + str(locnts).replace('[', '').replace(']', '') + '.')

        return locnts


def tercornot(data):
    shouldbeterc = tercbase.copy()
    shouldbeterc = shouldbeterc.loc[(shouldbeterc['NAZWA'] == globname[0])]
    sterc = shouldbeterc.copy()

    if sterc.empty:
        print("[b] " + globname[0] + " nie występuje w systemie TERC. Usuwam klucz…")
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
            tercb = tercbase.loc[
                (tercbase['WOJ'] == float(globterc['województwo']))]

            if tercb.empty:
                print("[b] Miejscowość " + globname[0] +
                      " nie spełnia kryteriów TERC, więc identyfikator nie zostanie dołączony do szablonu." +
                      "Usuwam klucz…")
                del data['terc']
                return data

    print('[b] Miejscowość ' + globname[0] + ' spełnia kryteria TERC, więc identyfikator zostanie dołączony' +
          'do szablonu.')

    return data


def getqid(data):
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

    if x == []:

        query = """SELECT ?coord ?item ?itemLabel 
            WHERE
            {
              ?item wdt:P1653 '""" + terid + """'.
              OPTIONAL {?item wdt:P625 ?coord}.
              SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
            }"""

        generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
        x = list(generator)

        if x == []:
            try:
                print('[b] Ustawiono tryb domyślny NTS.')

                query = """SELECT ?coord ?item ?itemLabel 
                    WHERE
                    {
                      ?item wdt:P1653 '""" + ntsplease() + """'.
                      OPTIONAL {?item wdt:P625 ?coord}.
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                    }"""

                generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                x = list(generator)

            except KeyError:
                print('[b] ' + str(KeyError))
                print('[b] Domyślny tryb NTS nie zwrócił wyniku.')
                print('[b] Ustawiono niepewny tryb NTS.')

                for i in range(len(ntsplease(mode='uncertain'))):

                    query = """SELECT ?coord ?item ?itemLabel 
                        WHERE
                        {
                          ?item wdt:P1653 '""" + ntsplease(mode='uncertain')[i] + """'.
                          OPTIONAL {?item wdt:P625 ?coord}.
                          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                        }"""

                    generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
                    x = list(generator)

                    if x != []:
                        changemode(1)
                        break

            if x == []:
                raise KeyError('Nic nie znalazłem w Wikidata. [b]')

    string = ''.join(map(str, x))
    qidentificator = string.replace("[[wikidata:", "").replace("]]", "")
    qidl = {'wikidata': qidentificator}
    everythingiknow.update(qidl)
    print('[b] (::) QID:  ' + str(qidentificator))
    return qidentificator


site = pwbot.Site("wikidata", "wikidata")
repo = site.data_repository()


def coords(qid):
    item = pwbot.ItemPage(repo, qid)

    try:
        item.get()

    except pwbot.exceptions.MaxlagTimeoutError:
        item.get()

    if item.claims:
        item = pwbot.ItemPage(repo, qid)  # This will be functionally the same as the other item we defined
        item.get()

        if 'P625' in item.claims:
            coordinates = item.claims['P625'][0].getTarget()

            # Couldn't see any other way.
            latitude = coordinates.lat
            longitude = coordinates.lon
            coordins = {'koordynaty': str(latitude) + ', ' + str(longitude)}
            everythingiknow.update(coordins)

    return tercornot(everythingiknow)  # ;)
