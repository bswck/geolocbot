#!/usr/bin/python
# -*- coding: utf-8 -*-

# Pywikibot will automatically set the user-agent to include your username.
# To customise the user-agent see
# https://www.mediawiki.org/wiki/Manual:Pywikibot/User-agent

import pywikibot as pwbot
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator
from pywikibot.bot import SingleSiteBot
from pywikibot import pagegenerators as pg
from coordinates import Coordinate

# Yet!
everythingiknow = {}


def getqid(data):
    sid = data['SIMC']

    # Please don't confuse with 'Lidl'. :D
    sidl = {'simc': sid}
    everythingiknow.update(sidl)

    terid = data['TERC']
    teridl = {'terc': terid}
    everythingiknow.update(teridl)

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
    print('[bot] (::) QID: ' + str(qidentificator))
    return qidentificator


site = pwbot.Site("wikidata", "wikidata")
repo = site.data_repository()


def coords(qid):
    item = pwbot.ItemPage(repo, qid)
    item.get()

    if item.claims:
        item = pwbot.ItemPage(repo, qid)  # This will be functionally the same as the other item we defined
        item.get()

        if 'P625' in item.claims:
            coordinates = item.claims['P625'][0].getTarget()
            coords = str(coordinates)

            # Couldn't see any other way.
            latitude = str(coords[(coords.find('"latitude": ') + 12):(coords.find('"longitude"') - 4)]).replace(',\n', '') + '° N,'
            longitude = str(coords[(coords.find('"longitude": ') + 13):(coords.find('"precision"') - 4)]).replace(',\n', '') + '° W'
            coords = {'szerokosc': latitude, 'dlugosc': longitude}
            everythingiknow.update(coords)
            return everythingiknow  # ;)
