# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import sys
import time
import pywikibot as pwbot
from __init__ import geolocbot
from getcats import cleanup_getcats, run
from databases import cleanup_databases, simc_database_search, encode_to_terc, updatename
from pywikibot import InvalidTitle
from querying import geolocbotQuery, cleanup_querying, coords, change_mode


def session_clean():
    geolocbot.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
    cleanup_databases()
    cleanup_getcats()
    cleanup_querying()


site = geolocbot.site
start = []


def save_info(page, data):
    geolocbot.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
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

    change_mode()


def check_title(pagename):
    geolocbot.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
    pagename_corrected = pagename

    if pagename.find(':') != -1:
        from2index = ''
        for i in pagename:

            if i == ':':
                from2index = pagename.find(i) + 1

        # Prints out that namespace name has been excluded from the pagename.
        geolocbot.output("Usunięto '" + pagename[:from2index] + "'.")

        pagename_corrected = str(pagename[from2index::])
        check_title(pagename_corrected)

    pagename_corrected = pagename_corrected[0].upper() + pagename_corrected[1::]

    page = pwbot.Page(site, pagename_corrected)

    if page.isRedirectPage():
        geolocbot.output('To jest przekierowanie.')
        pagename_corrected = str(page.getRedirectTarget()).replace('[[', '') \
            .replace(']]', '') \
            .replace('nonsensopedia:', '') \
            .replace('pl:', '')

        if '#' in pagename_corrected:
            for char in pagename_corrected:

                if char == '#':
                    sharpindex = pagename_corrected.find(char)
                    pagename_corrected = pagename_corrected[:sharpindex]

        geolocbot.output(f'Cel przekierowania to [[{pagename_corrected}]].')

    # Return the corrected pagename string.
    return pagename_corrected


# This runs the whole code.
def main(pagename='unpreloaded'):
    geolocbot.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
    session_clean()

    try:
        if pagename == 'unpreloaded':
            pagename = geolocbot.input('Podaj nazwę artykułu: ')

            if isinstance(pagename, geolocbot.goThroughList):
                articles = geolocbot.list()

                for article in articles:
                    main(pagename=article)

            r = time.time()

            if start:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            pagename = check_title(pagename)

        else:
            r = time.time()

            if start:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            geolocbot.output('Przetwarzam stronę z listy (' + str(pagename) + ').')

        updatename(pagename)
        data = simc_database_search(encode_to_terc(run(pagename)))

        # The question is: "haven't you made a mistake whilst inputing?".
        if data is None:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

        else:
            data = coords(geolocbotQuery.get_Q_id(data))

        if pagename != 'unpreloaded':
            geolocbot.unhook(pagename,
                             str(data).replace('{', '').replace('}', '').replace(': ', ' – ').replace("'", ''))

    except ValueError as value_error_hint:
        geolocbot.outputAndForward.value_error(value_error_hint, pagename)
        main() if pagename == 'unpreloaded' else None

    except KeyError as key_error_hint:
        geolocbot.outputAndForward.key_error(key_error_hint, pagename)
        main() if pagename == 'unpreloaded' else None

    except geolocbot.exceptions.TooManyRows as too_many_rows_hint:
        geolocbot.outputAndForward.too_many_rows_error(too_many_rows_hint, pagename)
        main() if pagename == 'unpreloaded' else None

    except InvalidTitle:
        geolocbot.outputAndForward.invalid_title_error()
        main() if pagename == 'unpreloaded' else None

    except KeyboardInterrupt:
        geolocbot.outputAndForward.keyboard_interrupt_error()
        answer = geolocbot.input().upper()
        possible_answers = ['T', 'N']

        while answer not in possible_answers:
            answer = geolocbot.input('Odpowiedź <T/N>: ').upper()

        if answer == 'T':
            print()
            main(pagename=pagename)

        else:
            geolocbot.end()

    except pwbot.exceptions.MaxlagTimeoutError:
        main(pagename=pagename)

    except SystemExit:
        sys.exit()

    except:
        geolocbot.forward_error(sys.exc_info()[0].__name__, 'Oops, wystąpił nieznany błąd.')
        main() if pagename == 'unpreloaded' else None

    else:
        print()
        show = str(data).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')
        geolocbot.output('Pobrano: ' + show)

        try:
            save_info(pwbot.Page(site, pagename), data)

        except pwbot.exceptions.MaxlagTimeoutError:
            save_info(pwbot.Page(site, pagename), data)

        finally:
            return data
