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
from info_from_categories_generator import geolocbotDirectlyFromArticle
from databases_search_engine import geolocbotDatabases
from pywikibot import InvalidTitle
from wikidata_queries_generator import geolocbotQuery


site = geolocbotMain.site


class geolocbotTask(object):
    def __init__(self):
        self.data_to_display = ''
        self.start = []

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
        occuring_aliases = []
        places = []

        place = len(text)

        for alias in category_aliases:
            if alias in text_lower:
                occuring_aliases.append(alias)
                occuring_aliases = list(set(occuring_aliases))

        if len(occuring_aliases) == 1:
            place = text_lower.find(occuring_aliases[0])
            del occuring_aliases[0]

        elif len(occuring_aliases) > 2:
            for occurence in range(len(occuring_aliases)):
                places.append(int(occurence))

            while occuring_aliases:
                del occuring_aliases[0]

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
            from2index = ''
            for i in pagename:

                if i == ':':
                    from2index = pagename.find(i) + 1

            # Prints out that namespace name has been excluded from the pagename.
            geolocbotMain.output("Usunięto '" + pagename[:from2index] + "'.")

            pagename_corrected = str(pagename[from2index::])
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
                        sharpindex = pagename_corrected.find(char)
                        pagename_corrected = pagename_corrected[:sharpindex]

            geolocbotMain.output(f'Cel przekierowania to [[{pagename_corrected}]].')

        # Return the corrected pagename string.
        return pagename_corrected

    # This runs the whole code.
    def run(self, pagename='unpreloaded'):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        # geolocbotTask.session_clean()

        try:
            if pagename == 'unpreloaded':
                pagename = geolocbotMain.input('Podaj nazwę artykułu: ')

                if self.start:
                    for i in range(len(self.start)):
                        del self.start[i]

                self.start.append(time.time())

                if isinstance(pagename, geolocbotMain.goThroughList):
                    geolocbotTask.run_from_list()

                pagename = geolocbotTask.check_title(pagename)

            else:
                if self.start:
                    for i in range(len(self.start)):
                        del self.start[i]

                self.start.append(time.time())

                geolocbotMain.output('Przetwarzam stronę z listy (' + str(pagename) + ').')

            geolocbotDatabases.updatename(pagename)
            data = geolocbotDatabases \
                .simc_database_search(geolocbotDatabases.encode_to_terc(geolocbotDirectlyFromArticle.run(pagename)))

            if data is None:
                raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

            else:
                data = geolocbotQuery.collect_geocoordinates(geolocbotQuery.SPARQL(data))

            if pagename != 'unpreloaded':
                geolocbotMain.unhook(pagename,
                                     str(data).replace('{', '').replace('}', '').replace(': ', ' – ').replace("'", ''))

        except ValueError as value_error_hint:
            geolocbotMain.outputAndForward.value_error(value_error_hint, pagename)
            geolocbotTask.run(pagename=pagename)

        except KeyError as key_error_hint:
            geolocbotMain.outputAndForward.key_error(key_error_hint, pagename)
            geolocbotTask.run(pagename=pagename)

        except geolocbotMain.exceptions.TooManyRows as too_many_rows_hint:
            geolocbotMain.outputAndForward.too_many_rows_error(too_many_rows_hint, pagename)
            geolocbotTask.run(pagename=pagename)

        except InvalidTitle:
            geolocbotMain.outputAndForward.invalid_title_error()
            geolocbotTask.run(pagename=pagename)

        except KeyboardInterrupt:
            geolocbotMain.outputAndForward.keyboard_interrupt_error()
            answer = geolocbotMain.input().upper()
            possible_answers = ['T', 'N']

            while answer not in possible_answers:
                answer = geolocbotMain.input('Odpowiedź <T/N>: ').upper()

            if answer == 'T':
                print()
                geolocbotTask.run(pagename=pagename)

            else:
                geolocbotMain.end()

        except pwbot.exceptions.MaxlagTimeoutError:
            geolocbotTask.run(pagename=pagename)

        except SystemExit:
            sys.exit()

        except:
            geolocbotMain.forward_error(sys.exc_info()[0].__name__, 'Oops, wystąpił nieznany błąd.')
            geolocbotTask.run(pagename=pagename)

        else:
            print()
            self.data_to_display = str(data).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')
            geolocbotMain.output('Pobrano: ' + self.data_to_display)

            try:
                geolocbotTask.save_info(pwbot.Page(site, pagename), data)

            except pwbot.exceptions.MaxlagTimeoutError:
                geolocbotTask.save_info(pwbot.Page(site, pagename), data)

            finally:
                return data

    @staticmethod
    def run_from_list():
        articles = geolocbotMain.list()

        for article in articles:
            geolocbotTask.run(pagename=article)


geolocbotTask = geolocbotTask()
