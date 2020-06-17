# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import sys
import requests as rq
import time
import pywikibot as pwbot
from __init__ import geolocbot
from getcats import run
from databases import filtersimc, terencode, TooManyRows, updatename
from pywikibot import InvalidTitle
from querying import coords, getqid, uncertain, changemode

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl
start = []


# Errors definitions.
class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass


def apply(page, data):
    text = page.text
    place = text.find('[[Kategoria:')
    if '[[Kategoria:' not in text:
        place = text.find('[[Category:')
    template = str('\n{{lokalizacja|' + data['koordynaty'] + '|simc=' + data['simc'] +
                   ('|terc=' + data['terc'] if 'terc' in data.keys() else str()) + '|wikidata=' + data['wikidata'] +
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
    st = pagename

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

        st = str(pagename[from2index::])
        checktitle(st)

    if " (" in pagename:
        for i in pagename:

            if i == '(':
                fromindex = pagename.find(i) - 1
                geolocbot.output("Usunięto dopisek '" + pagename[fromindex + 1:] + "'.")

    # .capitalize() changes further characters to lower,
    # that is why I use this method.
    # For example, if I used .capitalize(),
    # "ruciane-Nida" would be converted into "Ruciane-nida",
    # which is uncorrect.
    st = st[0].upper() + st[1::]

    # Return the corrected pagename string.
    return st


def end():
    geolocbot.output('Zapraszam ponownie!')
    print('-*-*-*')
    sys.exit()


# This runs the whole code.
def main(pagename=None):
    try:
        if pagename is None:
            pagename = input('-b- Podaj nazwę artykułu: ')

            end() if '*e' in pagename else None

            geolocbot.output('Zaczynam odmierzać czas.')
            r = time.time()

            if start != []:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            pagename = checktitle(pagename)
        else:

            geolocbot.output('Zaczynam odmierzać czas.')
            r = time.time()

            if start != []:
                for i in range(len(start)):
                    del start[i]

            start.append(r)

            geolocbot.output('Nazwa artykułu (' + pagename + ') w pamięci.')

        updatename(pagename)
        data = filtersimc(terencode(run(pagename)))

        # The question is: "haven't you made a mistake whilst inputing?".
        if data is None:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

        else:
            data = coords(getqid(data))

    except ValueError:
        geolocbot.exceptions.ValueErr(pagename)
        main()

    except KeyError:
        geolocbot.exceptions.ValueErr(pagename)
        main()

    except TooManyRows:
        geolocbot.exceptions.TooManyRowsErr(TooManyRows)
        main()

    except InvalidTitle:
        geolocbot.exceptions.InvalidTitleErr(InvalidTitle)
        main()

    except EmptyNameError:
        geolocbot.exceptions.EmptyNameErr()
        main()

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
            end()

    except pwbot.exceptions.MaxlagTimeoutError:
        main(pagename=pagename)

    except SystemExit:
        sys.exit()

    except:
        geolocbot.err(sys.exc_info()[0].__name__, 'Oops, wystąpił nieznany błąd.')
        main()

    else:
        print()
        show = str(data).replace('{', '').replace('}', '').replace(': ', ' → ').replace("'", '')
        geolocbot.output('Pobrano: ' + show)

        try:
            apply(pwbot.Page(site, 'Użytkownik:Stim/' + pagename), data)

        except pwbot.exceptions.MaxlagTimeoutError:
            apply(pwbot.Page(site, 'Użytkownik:Stim/' + pagename), data)

        finally:
            return data
