#!/usr/bin/python
# -*- coding: utf-8 -*-

# Pywikibot will automatically set the user-agent to include your username.
# To customise the user-agent see
# https://www.mediawiki.org/wiki/Manual:Pywikibot/User-agent

import pywikibot as pwbot
import pandas as pd
from databases import globname, globterc
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator
from pywikibot.bot import SingleSiteBot
from pywikibot import pagegenerators as pg
from coordinates import Coordinate

# Yet!
everythingiknow = {}

tercbase = pd.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])


def tercornot(data):
    shouldbeterc = tercbase.copy()
    shouldbeterc = shouldbeterc.loc[(shouldbeterc['NAZWA'] == globname[0])]
    sterc = shouldbeterc.copy()

    if sterc.empty:
        print("[bot] " + globname[0] + " nie występuje w systemie TERC. Usuwam klucz…")
        del data['terc']
        return data

    sterc = sterc.loc[
        (sterc['WOJ'] == float(globterc['województwo'])) & (sterc['POW'] == float(globterc['powiat'])) & (sterc['GMI'] == float(globterc['gmina']))]

    if shouldbeterc.empty:
        shouldbeterc = shouldbeterc.loc[
            (shouldbeterc['WOJ'] == float(globterc['województwo'])) & (shouldbeterc['POW'] == float(int(globterc['powiat'])))]

        if shouldbeterc.empty:
            tercb = tercbase.loc[
                (tercbase['WOJ'] == float(globterc['województwo']))]
            print(tercbase)

            if tercb.empty:
                print("[bot] Miejscowość " + globname[0] + " nie spełnia kryteriów TERC, więc identyfikator nie zostanie dołączony do szablonu. Usuwam klucz…")
                del data['terc']
                return data

    print('[bot] Miejscowość ' + globname[0] + ' spełnia kryteria TERC, więc identyfikator zostanie dołączony do szablonu.')

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
        wikidata_site = pwbot.Site("wikidata", "wikidata")
        generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
        x = list(generator)

        if x == []:
            raise KeyError('Albo jestem głupi, albo nic nie ma w Wikidata. [bot]')

    string = ''.join(map(str, x))
    qidentificator = string.replace("[[wikidata:", "").replace("]]", "")
    qidl = {'wikidata': qidentificator}
    everythingiknow.update(qidl)
    print('[bot] (::) QID:  ' + str(qidentificator))
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
            coords = {'koordynaty': str(latitude) + ', ' + str(longitude)}
            everythingiknow.update(coords)

    return tercornot(everythingiknow)  # ;)
