# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import sys
import time
import pywikibot as pwbot
from __init__ import geolocbotMain
from needs_repair.info_from_categories_generator import geolocbotDirectlyFromArticle
from needs_repair.databases_search_engine import geolocbotDatabases
from pywikibot import InvalidTitle
from needs_repair.wikidata_queries_generator import geolocbotQuery


site = geolocbotMain.site


class geolocbotTask(object):
    def __init__(self):
        self.data = {}
        self.running_from_list = False
        self.end = int()
        self.data_to_display = ''
        self.start = int()
        self.occuring_aliases = []
        self.pagename = ''
        self.already_done = []
        self.articles = []

    @staticmethod
    def session_clean():
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        geolocbotDatabases.cleanup_databases()
        geolocbotDirectlyFromArticle.cleanup_getcats()
        geolocbotQuery.cleanup_queries_generator()

    def save_info(self, page, data):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        text = page.text

        text_lower = text.lower()
        category_aliases = ['[[category:', '[[kategoria:']
        places = []

        place = len(text)

        self.occuring_aliases = []

        for alias in category_aliases:
            if alias in text_lower:
                self.occuring_aliases.append(alias)
                self.occuring_aliases = list(set(self.occuring_aliases))

        if len(self.occuring_aliases) == 1:
            place = text_lower.find(self.occuring_aliases[0])

        elif len(self.occuring_aliases) > 2:
            for occurence in range(len(self.occuring_aliases)):
                places.append(int(occurence))

            place = min(places)

        template = str('{{lokalizacja|' + data['koordynaty'] + '|simc=' + data['simc'] +
                       ('|terc=' + data['terc'] if 'terc' in data.keys() else str()) + '|wikidata=' + data[
                           'wikidata'] +
                       ('' if not geolocbotQuery.uncertain else '|niepewne=1') + '}}\n')

        if '{{lokalizacja|' in text:
            templace = text.find('{{lokalizacja|')
            page.text = text.replace(text[templace:place], template.replace('\n', '') + '\n')
            page.save('/* zastąpiono */ ' + self.data_to_display)

        else:
            page.text = text[:place] + template + text[place:]
            page.save('/* dodano */ ' + self.data_to_display)

        geolocbotQuery.change_mode()

    @staticmethod
    def check_title(pagename):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        pagename_corrected = pagename

        if pagename.find(':') != -1:
            index_to_delete_from = ''
            for i in pagename:

                if i == ':':
                    index_to_delete_from = pagename.find(i) + 1

            # Prints out that namespace name has been excluded from the pagename.
            geolocbotMain.output("Usunięto '" + pagename[:index_to_delete_from] + "'.")

            pagename_corrected = str(pagename[index_to_delete_from::])
            geolocbotTask.check_title(pagename_corrected)

        pagename_corrected = pagename_corrected[0].upper() + pagename_corrected[1::]

        page = pwbot.Page(site, pagename_corrected)

        if page.isRedirectPage():
            geolocbotMain.output('To jest przekierowanie.')
            pagename_corrected = str(page.getRedirectTarget()).replace('[[', '') \
                .replace(']]', '') \
                .replace('nonsensopedia:', '') \
                .replace('pl:', '')

            if '#' in pagename_corrected:
                for char in pagename_corrected:

                    if char == '#':
                        sharp_index = pagename_corrected.find(char)
                        pagename_corrected = pagename_corrected[:sharp_index]

            geolocbotMain.output(f'Cel przekierowania to [[{pagename_corrected}]].')

        # Return the corrected pagename string.
        return pagename_corrected

    def run_tasks(self, pagename):
        if isinstance(pagename, geolocbotMain.goThroughList):
            geolocbotTask.run_from_list()

        self.pagename = geolocbotTask.check_title(self.pagename)
        geolocbotMain.output(f'Przetwarzam stronę z listy ({self.pagename}).')

        geolocbotDatabases.updatename(self.pagename)
        data = geolocbotDatabases \
            .simc_database_search(geolocbotDatabases.encode_to_terc(geolocbotDirectlyFromArticle.run(pagename)))

        data = geolocbotQuery.collect_geocoordinates(geolocbotQuery.SPARQL(data))

        geolocbotMain.unhook(pagename, str(data)
                             .replace('{', '')
                             .replace('}', '')
                             .replace(': ', ' – ')
                             .replace("'", ''))

        geolocbotTask.time_info()
        self.data = data

    def page_name_request(self):
        self.pagename = geolocbotMain.input('Podaj nazwę artykułu: ')
        self.start = time.time()

    def run(self, pagename=geolocbotMain.notProvided()):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        geolocbotTask.session_clean()
        self.already_done.append(self.pagename)

        try:
            if self.running_from_list:
                pagename_occurences = list(filter(lambda name: name == self.pagename, self.already_done))
                occurences = 0

                for occurence in range(len(pagename_occurences)):
                    occurences += occurence ** 0

                geolocbotMain.debug.output(self.already_done)

                if occurences < 2:
                    geolocbotTask.run_tasks(self.pagename)

                else:
                    self.pagename = self.articles[self.articles.index(self.pagename) + 1]
                    geolocbotTask.run_tasks(self.pagename)

            elif isinstance(pagename, geolocbotMain.notProvided):
                geolocbotTask.page_name_request()
                geolocbotTask.run_tasks(self.pagename)

        except ValueError as value_error_hint:
            self.already_done.append(self.pagename)
            geolocbotMain.outputAndForward.value_error(value_error_hint, self.pagename)
            geolocbotTask.run()

        except KeyError as key_error_hint:
            self.already_done.append(self.pagename)
            geolocbotMain.outputAndForward.key_error(key_error_hint, self.pagename)
            geolocbotTask.run()

        except geolocbotMain.exceptions.TooManyRows as too_many_rows_hint:
            self.already_done.append(self.pagename)
            geolocbotMain.outputAndForward.too_many_rows_error(too_many_rows_hint, self.pagename)
            geolocbotTask.run()

        except InvalidTitle:
            geolocbotMain.outputAndForward.invalid_title_error()
            geolocbotTask.run()

        except KeyboardInterrupt:
            geolocbotMain.outputAndForward.keyboard_interrupt_error()
            answer = geolocbotMain.input().upper()
            possible_answers = ['T', 'TA', 'TAK', 'N', 'NI', 'NIE']

            while answer not in possible_answers:
                answer = geolocbotMain.input('Odpowiedź <T(ak)/N(ie)>: ').upper()

            if answer in possible_answers[:3]:
                geolocbotTask.run()

            else:
                geolocbotMain.end()

        except pwbot.exceptions.MaxlagTimeoutError:
            geolocbotTask.run()

        except SystemExit:
            sys.exit()

        except:
            geolocbotMain.forward_error(sys.exc_info()[0].__name__, 'Oops, wystąpił nieprzewidziany błąd.')
            geolocbotTask.run()

        else:
            print()
            self.data_to_display = str(self.data)\
                .replace('{', '')\
                .replace('}', '')\
                .replace(': ', ' → ')\
                .replace("'", '')
            geolocbotMain.output('Pobrano: ' + self.data_to_display)

            try:
                geolocbotTask.save_info(pwbot.Page(site, self.pagename), self.data)

            except pwbot.exceptions.MaxlagTimeoutError:
                geolocbotTask.save_info(pwbot.Page(site, self.pagename), self.data)

            finally:
                geolocbotTask.time_info()
                self.data = {}

    def run_from_list(self):
        self.running_from_list = True
        self.articles = geolocbotMain.list()
        self.pagename = self.articles[0]
        geolocbotTask.run()

        if len(self.already_done) == len(self.articles):
            self.articles = []
            self.already_done = []
            self.running_from_list = False

        geolocbotTask.run()

    def time_info(self):
        self.end = time.time()
        time_taken = (self.end - self.start)
        time_to_print = "%.1f" % time_taken
        geolocbotMain.output(f"Czas operacyjny: {time_to_print.replace('.', ',')}s.")


geolocbotTask = geolocbotTask()
