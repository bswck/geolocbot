# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import sys
import time
import pywikibot as pwbot
from __init__ import geolocbot, EmptyNameError
from getcats import cleanup_getcats, run
from databases import cleanup_databases, gapterc, filtersimc, terencode, TooManyRows, updatename
from pywikibot import InvalidTitle
from querying import cleanup_querying, coords, getqid, uncertain, changemode


def session_clean():
    cleanup_databases()
    cleanup_getcats()
    cleanup_querying()


site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl
start = []


def apply(page, data):
    text = page.text
    place = len(text) - 1

    text_lower = text.lower()
    category_aliases = ['[[category:', '[[kategoria:']
    occuring_aliases = []
    places = []

    place = len(text)

    for alias in category_aliases:
        if alias in text:
            occuring_aliases.append(alias)
            occuring_aliases = list(set(occuring_aliases))

    if occuring_aliases == 1:
        place = text.find(alias)

    elif occuring_aliases > 2:
        for occurence in range(len(occuring_aliases)):
            places.append(int(occurence))

        place = min(places)

    template = str('{{lokalizacja|' + data['koordynaty'] + '|simc=' + data['simc'] +
                   ('|terc=' + data['terc'] if 'terc' in data.keys() else str()) + '|wikidata=' + data[
                       'wikidata'] +
                   ('' if uncertain == [] else '|niepewne=1') + '}}\n')

    if '{{lokalizacja|' in text:
        templace = text.find('{{lokalizacja|')
        page.text = text.replace(text[templace:place], template.replace('\n', '') + '\n')
        page.save('/* zastąpiono */ ' + template)

    else:
        page.text = text[:place] + template + text[place:]
        page.save('/* dodano */ ' + template)

    changemode()


# Function checktitle checks if the providen title is valid.
def checktitle(pagename):
    # Check if the title isn't an empty string.
    # (I don't think that any other whitespaces can appear).
    if len(pagename) == 0 or pagename == ' ' * len(pagename):
        raise EmptyNameError

    # I'm putting the title into two strings:
    # * st is the corrected title,
    # * pagename is the title input at the beginning.
    pagename_corrected = pagename

    # This condition erases namespaces from the pagename.
    # For example, if "Kategoria:Województwo śląskie" has been input,
    # this will take it as "Województwo śląskie" instead.
    if pagename.find(':') != -1:
        from2index = ''
        for i in pagename:

            if i == ':':
                from2index = pagename.find(i) + 1

        # Prints out that namespace name has been excluded from the pagename.
        geolocbot.output("Usunięto '" + pagename[:from2index] + "'.")

        pagename_corrected = str(pagename[from2index::])
        checktitle(pagename_corrected)

    # .capitalize() changes further characters to lower,
    # that is why I use this method.
    # For example, if I used .capitalize(),
    # "ruciane-Nida" would be converted into "Ruciane-nida",
    # which is uncorrect.
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

        geolocbot.output('Cel przekierowania to [[' + str(pagename_corrected) + ']].')

    # Return the corrected pagename string.
    return pagename_corrected


# This runs the whole code.
def main(pagename='unpreloaded'):
    session_clean()

    try:
        if pagename == 'unpreloaded':
            pagename = geolocbot.input('Podaj nazwę artykułu: ', cannot_be_empty=True)

            if pagename == 'key::c3!*DZ+Tx!h2ua!X':
                articles = geolocbot.list()

                for article in articles:
                    main(pagename=article)

            r = time.time()

            if start != []:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            pagename = checktitle(pagename)

        else:
            r = time.time()

            if start != []:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            geolocbot.output('Przetwarzam stronę z listy (' + str(pagename) + ').')

        updatename(pagename)
        data = filtersimc(terencode(run(pagename)))

        # The question is: "haven't you made a mistake whilst inputing?".
        if data is None:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

        else:
            data = coords(getqid(data))

        if pagename != 'unpreloaded':
            geolocbot.unhook(pagename,
                             str(data).replace('{', '').replace('}', '').replace(': ', ' – ').replace("'", ''))

    except ValueError as ve:
        geolocbot.exceptions.ValueErr(ve, pagename)
        geolocbot.delete_template()
        main() if pagename == 'unpreloaded' else None

    except KeyError as ke:
        geolocbot.exceptions.KeyErr(ke, pagename)
        main() if pagename == 'unpreloaded' else None

    except TooManyRows as tmr:
        geolocbot.exceptions.TooManyRowsErr(tmr, pagename)
        main() if pagename == 'unpreloaded' else None

    except InvalidTitle:
        geolocbot.exceptions.InvalidTitleErr()
        main() if pagename == 'unpreloaded' else None

    except KeyboardInterrupt:
        geolocbot.exceptions.KeyboardInterruptErr()
        ct = geolocbot.input().upper()
        ans = ['T', 'N']

        while ct not in ans:
            ct = geolocbot.input('Odpowiedź <T/N>: ').upper()

        if ct == 'T':
            print()
            main(pagename=pagename)

        else:
            geolocbot.end()

    except pwbot.exceptions.MaxlagTimeoutError:
        main(pagename=pagename)

    except EmptyNameError:
        geolocbot.exceptions.EmptyNameErr()
        main() if pagename == 'unpreloaded' else None

    except SystemExit:
        sys.exit()

    except:
        geolocbot.err(sys.exc_info()[0].__name__, 'Oops, wystąpił nieznany błąd.')
        main() if pagename == 'unpreloaded' else None

    else:
        print()
        show = str(data).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')
        geolocbot.output('Pobrano: ' + show)

        try:
            apply(pwbot.Page(site, pagename), data)

        except pwbot.exceptions.MaxlagTimeoutError:
            apply(pwbot.Page(site, pagename), data)

        finally:
            return data
