# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import pywikibot as pwbot
from __init__ import geolocbotMain
from databases_search_engine import geolocbotDatabases

site = geolocbotMain.site  # we're on nonsa.pl


class geolocbotDirectlyFromArticle(object):
    def __init__(self):
        self.captured = {}
        self.p = []
        self.getcats_fors = []
        self.be_careful = []

    def cleanup_getcats(self):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        if self.captured != {}:
            for key_value in list(self.captured.keys()):
                del self.captured[key_value]

        while p:
            del p[0]

        while be_careful:
            del be_careful[0]

    def collect_information_from_categories(self, article_categories, title):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        for i in range(len(article_categories)):
            page = pwbot.Page(site, title)
            text = page.text

            if "osiedl" in text[:250] or "dzielnic" in text[:250]:
                if not self.p:
                    print()
                    geolocbotMain.output("-" * (73 // 2) + "UWAGA!" + "-" * ((73 // 2) + 1))
                    geolocbotMain.output(
                        '(nonsa.pl) [TooManyRows]: Artykuł prawdopodobnie dotyczy osiedla lub dzielnicy.')
                    geolocbotMain.output("-" * 79)
                    print()
                    self.p.append(' ')

            # Checks if the category contains "Gmina".
            if 'gmina' not in self.captured and "Kategoria:Gmina " in article_categories[i]:
                gmina = article_categories[i].replace("Kategoria:Gmina ", "")  # (No need for namespace and type name).
                self.raise_categories(article_categories[i])
                add = {"gmina": gmina}
                self.captured.update(add)

            # Checks if the category contains "Powiat "; disclaiming category "Powiaty".
            elif 'powiat' not in self.captured and "Kategoria:Powiat " in article_categories[i]:
                powiat = article_categories[i].replace("Kategoria:Powiat ", "")
                self.raise_categories(article_categories[i])
                add = {"powiat": powiat.lower()}
                self.captured.update(add)

            # Checks if the category contains "Województwo ".
            elif 'województwo' not in self.captured and "Kategoria:Województwo " in article_categories[i]:
                wojewodztwo = article_categories[i].replace("Kategoria:Województwo ", "")
                add = {"województwo": wojewodztwo.upper()}
                self.captured.update(add)

            # Exceptions.
            elif "Kategoria:Ujednoznacznienia" in article_categories[i]:
                raise ValueError('Podana strona to ujednoznacznienie.')

            # Reading the category of category if it's one of these below.
            elif ("Kategoria:Miasta w" in article_categories[i] or "Kategoria:Powiaty w" in article_categories[
                i] or "Kategoria:Gminy w" in article_categories[i] or
                  "Kategoria:" + title in article_categories[i]) and (
                    'powiat' not in self.captured or 'gmina' not in self.captured):

                if geolocbotDatabases.check_status('powiat', title) is not False:
                    powiat = geolocbotDatabases.check_status('powiat', title)
                    add = {"powiat": powiat}
                    self.captured.update(add)

                if geolocbotDatabases.check_status('gmina', title) is not False:
                    gmina = geolocbotDatabases.check_status('gmina', title)
                    add = {"gmina": gmina}
                    self.captured.update(add)

                self.raise_categories(article_categories[i])

            else:
                if article_categories[i] not in be_careful:
                    be_careful.append(article_categories[i])
                    self.raise_categories(article_categories[i])

    @staticmethod
    def raise_categories(page_name):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        article_categories = [
            cat.title()
            for cat in pwbot.Page(site, page_name).categories()
            if 'hidden' not in cat.categoryinfo
        ]

        geolocbotDirectlyFromArticle.collect_information_from_categories(article_categories, page_name)
        return article_categories

    def run(self, page_name):
        geolocbotMain.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
        page = pwbot.Page(site, page_name)
        text = page.text

        if text == '':
            raise KeyError('Nie ma takiej strony.')

        self.raise_categories(page_name)  # script starts
        geolocbotMain.output('Z kategorii artykułu mam następujące dane:')
        geolocbotMain.output('województwo: {0}.'.format(
            (self.captured['województwo'].lower() if 'województwo' in list(self.captured.keys()) else '–')))
        geolocbotMain.output('powiat: {0}.'.format((self.captured['powiat'] if 'powiat' in list(self.captured.keys())
                                                    else '–')))
        geolocbotMain.output('gmina: {0}.'.format((self.captured['gmina'] if 'gmina' in list(self.captured.keys())
                                                   else '–')))
        line = {"NAZWA": page_name}
        self.captured.update(line)
        return self.captured


geolocbotDirectlyFromArticle = geolocbotDirectlyFromArticle()
