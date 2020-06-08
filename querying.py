# Generated using "<code>" button @ query.wikidata.org.
# --------
# !/usr/bin/python
# -*- coding: utf-8 -*-

# Pywikibot will automatically set the user-agent to include your username.
# To customise the user-agent see
# https://www.mediawiki.org/wiki/Manual:Pywikibot/User-agent

import pywikibot
import pandas as pd
from getcats import site
from pywikibot.pagegenerators import WikidataSPARQLPageGenerator
from pywikibot.bot import SingleSiteBot
from functions import main

class WikidataQueryBot(SingleSiteBot):
    """
    Basic bot to show wikidata queries.

    See https://www.mediawiki.org/wiki/Special:MyLanguage/Manual:Pywikibot
    for more information.
    """

    def __init__(self, generator, **kwargs):
        """
        Initializer.

        @param generator: the page generator that determines on which pages
            to print
        @type generator: generator
        """
        super(WikidataQueryBot, self).__init__(**kwargs)
        self.generator = generator

    def treat(self, page):
        print(page)


def ask(data):
    sym = str(data.at[0, 'SYM'])

    if __name__ == '__main__':
        query = """SELECT ?coord ?SIMC_place_ID ?item ?itemLabel WHERE {
      ?item wdt:P4046 '""" + sym + """'.
      OPTIONAL { ?item wdt:P625 ?coord. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
    }"""
        gen = WikidataSPARQLPageGenerator(query, site=site.data_repository())
        bot = WikidataQueryBot(gen, site=site)
        bot.run()


print(ask(main('Strzebiń')))
