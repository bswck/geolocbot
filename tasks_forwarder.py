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


def session_clean():
    geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
    geolocbotDatabases.cleanup_databases()
    geolocbotDirectlyFromArticle.cleanup_getcats()
    geolocbotQuery.cleanup_querying()


site = geolocbotMain.site


class geolocbotTask(object):
    def __init__(self):
        self.data_to_display = ''
        self.start = []

    @staticmethod
    def save_info(page, data):
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
            page.save('/* zastąpiono */ ' + template)

        else:
            page.text = text[:place] + template + text[place:]
            page.save('/* dodano */ ' + template)

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
    def main(self, pagename='unpreloaded'):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        session_clean()

        try:
            if pagename == 'unpreloaded':
                pagename = geolocbotMain.input('Podaj nazwę artykułu: ')

                if isinstance(pagename, geolocbotMain.goThroughList):
                    articles = geolocbotMain.list()

                    for article in articles:
                        geolocbotTask.main(pagename=article)

                r = time.time()

                if self.start:
                    for i in range(len(self.start)):
                        del self.start[i]

                self.start.append(r)

                pagename = geolocbotTask.check_title(pagename)

            else:
                r = time.time()

                if self.start:
                    for i in range(len(self.start)):
                        del self.start[i]

                self.start.append(r)

                geolocbotMain.output('Przetwarzam stronę z listy (' + str(pagename) + ').')

            geolocbotDatabases.updatename(pagename)
            data = geolocbotDatabases \
                .simc_database_search(geolocbotDatabases.encode_to_terc(geolocbotQuery.run(pagename)))

            if data is None:
                raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

            else:
                data = geolocbotQuery.coords(geolocbotQuery.get_Q_id(data))

            if pagename != 'unpreloaded':
                geolocbotMain.unhook(pagename,
                                     str(data).replace('{', '').replace('}', '').replace(': ', ' – ').replace("'", ''))

        except ValueError as value_error_hint:
            geolocbotMain.outputAndForward.value_error(value_error_hint, pagename)
            geolocbotTask.main() if pagename == 'unpreloaded' else None

        except KeyError as key_error_hint:
            geolocbotMain.outputAndForward.key_error(key_error_hint, pagename)
            geolocbotTask.main() if pagename == 'unpreloaded' else None

        except geolocbotMain.exceptions.TooManyRows as too_many_rows_hint:
            geolocbotMain.outputAndForward.too_many_rows_error(too_many_rows_hint, pagename)
            geolocbotTask.main() if pagename == 'unpreloaded' else None

        except InvalidTitle:
            geolocbotMain.outputAndForward.invalid_title_error()
            geolocbotTask.main() if pagename == 'unpreloaded' else None

        except KeyboardInterrupt:
            geolocbotMain.outputAndForward.keyboard_interrupt_error()
            answer = geolocbotMain.input().upper()
            possible_answers = ['T', 'N']

            while answer not in possible_answers:
                answer = geolocbotMain.input('Odpowiedź <T/N>: ').upper()

            if answer == 'T':
                print()
                geolocbotTask.main(pagename=pagename)

            else:
                geolocbotMain.end()

        except pwbot.exceptions.MaxlagTimeoutError:
            geolocbotTask.main(pagename=pagename)

        except SystemExit:
            sys.exit()

        except:
            geolocbotMain.forward_error(sys.exc_info()[0].__name__, 'Oops, wystąpił nieznany błąd.')
            geolocbotTask.main() if pagename == 'unpreloaded' else None

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


geolocbotTask = geolocbotTask()
