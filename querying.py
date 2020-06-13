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


def getqid(data):
    sid = data['SIMC']
    terid = data['TERC']
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
            raise KeyError('Albo jestem głupi, albo nic nie ma w WikiData. [bot]')

    string = ''.join(map(str, x))
    qidentificator = string.replace("[[wikidata:", "").replace("]]", "")
    print(qidentificator)
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
            coordsd = dict(coords)
            return coordsd
