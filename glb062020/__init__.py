# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import pywikibot as pwbot
import pandas as pd
import traceback
import sys
import time
from pandas import DataFrame
from os import system, name


# Errors definitions.
class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass


tmr_database = []


class glb(object):
    def __init__(self):
        self.i = '>b< '
        self.o = '[b] '
        self.n = '(nonsa.pl) '
        self.history = []
        self.items_list_beginning = '<!-- początek listy -->\n'
        self.items_list_end = '<!-- koniec listy -->'
        self.site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl

    @staticmethod
    def tmr(dataframe=''):
        """Saving TooManyRows to call it"""
        tmr_database.append(dataframe)

    @staticmethod
    def clean_tmr():
        """Deleting TooManyRows DataFrame"""
        while tmr_database != []:
            del tmr_database[0]

    @staticmethod
    def clear():
        if name == 'nt':
            _ = system('cls')

        else:
            _ = system('clear')

    @staticmethod
    def end():
        """Closes the program"""
        geolocbot.output('Zapraszam ponownie!')
        print('---')
        exit()

    def delete_template(self, pagename, reason):
        """Deleting template as an update procedure"""
        delete_from = pwbot.Page(self.site, pagename)
        txt = delete_from.text

        if '{{lokalizacja' in txt:
            template = txt[txt.find('{{lokalizacja'):]
            template = template[:(template.find('}}') + 2)]
            delete_from.text = txt.replace(template, '')
            delete_from.save('/* aktualizacja */ usunięcie szablonu lokalizacja (' + str(reason) + ')')

    def input(self, input_message='Odpowiedź: ', cannot_be_empty=False):
        """Geolocbot's specific input method"""
        print()
        answer = input(str(self.i + input_message))
        self.history.append(answer)

        if cannot_be_empty:
            if answer == '' or answer == ' ' * len(answer):
                raise EmptyNameError

        else:
            if answer == '' or answer == ' ' * len(answer):
                answer = input(str(self.i + input_message))

        if '*' in answer:
            if '*e' in answer and '*c' not in answer and '*l' not in answer and '*h' not in answer:
                geolocbot.end()

            elif '*c' in answer and '*e' not in answer and '*l' not in answer and '*h' not in answer:
                geolocbot.clear()
                answer = geolocbot.input(input_message)

            elif '*h' in answer and '*e' not in answer and '*l' not in answer and '*c' not in answer:
                geolocbot.output('Po kolei wpisywałeś: {0}.'.format(
                    str(list(self.history)[::1]).replace('[', '').replace(']', '')))
                answer = geolocbot.input(input_message)

            elif '*l' in answer and '*e' not in answer and '*c' not in answer and '*h' not in answer:

                l_count = 0

                for l in range(len(self.history)):
                    if self.history[l] == '*l':
                        l_count += 1

                    return 'key::c3!*DZ+Tx!h2ua!X'

                if l_count < 1:
                    answer = geolocbot.input(input_message)

                else:
                    geolocbot.output('Coś kombinujesz, nie radzę. Wpisałeś komendę *l już ' + str(l_count) + ' raz.')
                    answer = geolocbot.input('Nieprzekombinowana odpowiedź: ')

            elif len(answer) >= 2:
                if answer[answer.find('*') + 1] not in ['c', 'e', 'l'] and '*l' not in self.history:
                    geolocbot.output('Niepoprawna komenda.')
                    answer = geolocbot.input()

            else:
                geolocbot.output('Niepoprawna komenda.')
                answer = geolocbot.input()

        return answer

    def output(self, output_message):
        """Geolocbot's specific output method"""
        print(self.o + str(output_message))

    def err(self, nmb, output_error_message, hint='', pgn=False):
        """Function printing, recognising and differentiating errors"""
        error = ['ValueError', 'KeyError', 'TooManyRows', 'InvalidTitle', 'EmptyNameError', 'KeyboardInterrupt']
        bug_errors = ['AssertionError',
                      'AttributeError',
                      'MemoryError',
                      'NameError',
                      'TypeError',
                      'IndentationError',
                      'IndexError',
                      'OverflowError',
                      'SyntaxError',
                      'TabError',
                      'UnboundLocalError']
        print(self.n + '[' + (error[nmb] if isinstance(nmb, int) else nmb) + ']: ' + output_error_message,
              file=sys.stderr)

        if pgn is not False:
            if isinstance(nmb, int) and error[nmb] == error[2]:
                geolocbot.unhook(pgn, '([[Dyskusja użytkownika:Stim/TooManyRows-log|TooManyRows]])')

            else:
                geolocbot.unhook(pgn, (output_error_message if hint == '' else hint))
            geolocbot.delete_template(pgn, output_error_message)

        if isinstance(nmb, int) and error[nmb] == error[2]:
            tmr = tmr_database[0]
            raw_name = str(tmr.at[0, 'NAZWA'])
            pagename = "'''[[" + str(pgn) + "]]'''\n"
            report_page = pwbot.Page(self.site, 'Dyskusja użytkownika:Stim/TooManyRows-log')
            text = report_page.text

            if raw_name not in text:
                how_many_indexes = tmr.shape[0]
                add = '\n\n\n<center>\n' + pagename + '{| class="wikitable sortable"\n|-\n! NAZWA !! SIMC\n|-'

                for index in range(how_many_indexes):
                    add = add + '\n| [[' + str(raw_name) + ']] || ' + str(tmr.at[index, 'SYM']) + '\n|-'

                add = add + '\n|}\n~~~~~\n</center>'
                report_page.text = text + add
                report_page.save(u'/* raport */ TooManyRows: ' + str(raw_name))

            geolocbot.clean_tmr()

        if not isinstance(nmb, int):

            if str(nmb) in bug_errors:
                report_page = pwbot.Page(self.site, 'Dyskusja użytkownika:Stim/geolocbot-bugs')
                text = report_page.text
                put_place = text.find('|}\n{{Stim}}')
                add = '| {{#vardefine:bugid|{{#expr:{{#var:bugid}} + 1}}}} {{#var:bugid}} || ' + \
                      str(nmb) + ' || <pre>' + str(traceback.format_exc()) + '</pre> || ~~~~~ || {{/p}}\n|-\n'
                report_page.text = text[:put_place] + add + text[put_place:]
                report_page.save(u'/* raport */ bugerror: ' + str(nmb))

    def list(self):
        page = pwbot.Page(self.site, 'Użytkownik:Stim/lokwikipedia')

        items_list = []
        items = page.text
        items = items[items.find(self.items_list_beginning) + len(self.items_list_beginning):]

        for char_index in range(len(items)):
            if items[char_index] == '*':
                if char_index != len(items):
                    item_row = items[char_index:]

                    if '{{/unhook' in item_row:
                        item_row = item_row[2:item_row.find(' {{/unhook')]

                    else:
                        item_row = item_row[2:item_row.find('\n')]

                    occurences = 1

                    for occurence in range(len(item_row)):
                        if item_row[occurence] == '*':
                            occurences += 1

                    if occurences > 1:
                        item_row = item_row[:item_row.find('\n*')]

                    if item_row[-1] == ' ':
                        item_row = item_row[:-1] + item_row[-1].replace(' ', '')

                    items_list.append(item_row.replace('[', '').replace(']', ''))

                else:
                    item_row = items[char_index:]

                    if '{{/unhook' in item_row:
                        item_row = item_row[2:item_row.find(' {{/unhook')]

                    else:
                        item_row = item_row[2:items.find(self.items_list_end)]

                    if item_row[-1] == ' ':
                        item_row = item_row[:-1] + item_row[-1].replace(' ', '')

                    items_list.append(item_row.replace('[', '').replace(']', ''))

        return items_list

    def unhook(self, pagename, message):
        page = pwbot.Page(self.site, 'Użytkownik:Stim/lista')
        message = message.replace('{', '').replace('}', '')
        to_unhook = page.text

        if pagename in to_unhook:
            unhook_row = to_unhook[to_unhook.find('* [[' + pagename + ']]\n'):]
            unhook_row = unhook_row[:unhook_row.find('\n')]

            if unhook_row == '':
                unhook_row = to_unhook[to_unhook.find('* [[' + pagename + ']] {{/unhook'):]
                unhook_row = unhook_row[:unhook_row.find('\n')]

            if '{{/unhook' in unhook_row:
                unhook_place = unhook_row.find(' {{/unhook|')
                unhook_put = unhook_row[unhook_place:unhook_row.find('}}')]
                replaced_unhook = unhook_row.replace(unhook_put, ' {{/unhook|' + str(message))
                page.text = to_unhook.replace(unhook_row, replaced_unhook)
                page.save('/* -+' + str(pagename) + ' (nowy w miejsce starego) */ ' + str(message))

            else:
                add = '* [[' + str(pagename) + ']] {{/unhook|' + str(message) + '}}'
                page.text = to_unhook.replace(unhook_row, add)
                page.save('/* +' + str(pagename) + ' */ ' + str(message))

    @staticmethod
    def intro():
        system('@echo off')
        system('title Google Chrome')
        geolocbot.clear()
        print("""
_________          ______           ______       _____ 
__  ____/_____________  /______________  /_________  /_
_  / __ _  _ \  __ \_  /_  __ \  ___/_  __ \  __ \  __/
/ /_/ / /  __/ /_/ /  / / /_/ / /__ _  /_/ / /_/ / /_  
\____/  \___/\____//_/  \____/\___/ /_.___/\____/\__/  

                                        Geolocbot 2020
        """)
        print()
        geolocbot.output('Ctrl + C przerywa wykonywanie operacji.')
        geolocbot.output('Wpisanie *c spowoduje wyczyszczenie ekranu.')
        geolocbot.output('Wpisanie *h spowoduje pokazanie historii wpisanych wartości, komend.')
        geolocbot.output('Wpisanie *e spowoduje zamknięcie programu.')
        geolocbot.output('Wpisanie *l spowoduje masowe przeoranie artykułów z listy na [[Użytkownik:Stim/lista]].')
        geolocbot.output('Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')

    class exceptions(object):
        """Geolocbot's specific exceptions"""

        @staticmethod
        def ValueErr(ve, pagename):
            print()
            geolocbot.err(0, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.",
                          hint=str(ve), pgn=pagename)
            time.sleep(2)

            print(
                " " * 11 + "Hint:" + " " * 9 +
                str(ve).replace("'", '') if str(ve) != '0' else " " * 11 + "Hint:" +
                                                                " " * 7 + 'Nic nie znalazłem. [b]')
            time.sleep(2)

        @staticmethod
        def KeyErr(ke, pagename):
            print()
            ke_show = str(ke).replace("'", '') if str(ke) != '0' else 'Nie odnaleziono informacji w którejkolwiek ' \
                                                                      'z baz danych.'
            geolocbot.err(1, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.",
                          hint=ke_show, pgn=pagename)
            ke = " " * 11 + "Hint:" + " " * 7 + str(ke).replace("'", '') if str(ke) != '0' else " " * 11 + "Hint:" + \
                                                                                                " " * 7 + 'Nic nie ' \
                                                                                                          'znalazłem.' \
                                                                                                          ' [b]'
            print(ke)
            time.sleep(2)

        @staticmethod
        def TooManyRowsErr(tmr, pagename):
            print()
            geolocbot.err(2, 'Więcej niż 1 rząd w odebranych danych!', pgn=pagename)
            print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
            print()
            print(tmr, file=sys.stderr)
            tmr_database.append(tmr)
            time.sleep(2)

        @staticmethod
        def InvalidTitleErr():
            print()
            geolocbot.err(3, "Podany tytuł jest nieprawidłowy.")
            time.sleep(2)

        @staticmethod
        def EmptyNameErr():
            print()
            geolocbot.err(4, "Nie podano tytułu strony.")
            time.sleep(2)

        @staticmethod
        def KeyboardInterruptErr():
            print()
            geolocbot.err(5, "Pomyślnie przerwano operację.")
            geolocbot.output('Kontynuować? <T/N>')

    class debug(object):
        """Printing style for debugging purposes"""

        def __init__(self):
            self.d = 'debug_info >> '

        def output(self, output_message):
            geolocbot.output(self.d + str(output_message))


geolocbot = glb()
"""Base class for specific Geolocbot operations"""
geolocbot.debug = geolocbot.debug()
geolocbot.exceptions = geolocbot.exceptions()
