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


site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl
tmr_database = []


class glb(object):
    def __init__(self):
        self.i = '>b< '
        self.o = '[b] '
        self.n = '(nonsa.pl) '

    @staticmethod
    def tmr(dataframe=''):
        """Saving TooManyRows to call it"""
        tmr_database.append(dataframe)

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

    def input(self, input_message='Odpowiedź: ', cannot_be_empty=False):
        """Geolocbot's specific input method"""
        answer = input(str(self.i + input_message))

        if cannot_be_empty:
            if answer == '' or answer == ' ' * len(answer):
                raise EmptyNameError

        if answer[0] == '*':
            if '*e' in answer:
                glb().end()

            elif '*c' in answer and '*e' not in answer:
                glb().clear()
                answer = geolocbot.input(input_message)

            elif len(answer) >= 2:
                if answer[1] not in ['c', 'e']:
                    geolocbot.output('Niepoprawna komenda.')
                    answer = geolocbot.input()

            else:
                geolocbot.output('Niepoprawna komenda.')
                answer = geolocbot.input()

        return answer

    def output(self, output_message):
        """Geolocbot's specific output method"""
        print(self.o + str(output_message))

    def err(self, nmb, output_error_message, tmr=False, pgn=False):
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

        if isinstance(nmb, int) and error[nmb] == error[2]:
            tmr = tmr_database[0]
            raw_name = str(tmr.at[0, 'NAZWA'])
            name = "'''[[" + str(pgn) + "]]'''\n"
            report_page = pwbot.Page(site, 'Dyskusja użytkownika:Stim/TooManyRows-log')
            text = report_page.text

            if raw_name not in text:
                how_many_indexes = tmr.shape[0]
                add = '\n\n\n<center>\n' + name + '{| class="wikitable sortable"\n|-\n! NAZWA !! SIMC\n|-'

                for index in range(how_many_indexes):
                    add = add + '\n| [[' + str(raw_name) + ']] || ' + str(tmr.at[index, 'SYM']) + '\n|-'

                add = add + '\n|}\n~~~~~\n</center>'
                report_page.text = text + add
                report_page.save(u'/* raport */ TooManyRows: ' + str(raw_name))
            del tmr_database[0]

        if not isinstance(nmb, int):

            if str(nmb) in bug_errors:
                report_page = pwbot.Page(site, 'Dyskusja użytkownika:Stim/geolocbot-bugs')
                text = report_page.text
                put_place = text.find('|}\n{{Stim}}')
                add = '| {{#vardefine:bugid|{{#expr:{{#var:bugid}} + 1}}}} {{#var:bugid}} || ' + \
                      str(nmb) + ' || <pre>' + str(traceback.format_exc()) + '</pre> || ~~~~~ || {{/p}}\n|-\n'
                report_page.text = text[:put_place] + add + text[put_place:]
                report_page.save(u'/* raport */ bugerror: ' + str(nmb))

    @staticmethod
    def intro():
        system('@echo off')
        system('title Geolocbot 2020 // Bot for Nonsensopedia // https://nonsa.pl/wiki/Strona_główna')
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
        glb().output('Ctrl + C przerywa wykonywanie operacji.')
        glb().output('CE:')
        glb().output('Wpisanie *c spowoduje wyczyszczenie ekranu.')
        glb().output('Wpisanie *e spowoduje zamknięcie programu.')
        glb().output('Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')
        print()

    class exceptions(object):
        """Geolocbot's specific exceptions"""

        @staticmethod
        def ValueErr(ve, pagename):
            print()
            glb().err(0, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")
            time.sleep(2)

            print(
                " " * 11 + "Hint:" + " " * 9 +
                str(ve).replace("'", '') if str(ve) != '0' else " " * 11 + "Hint:" +
                                                                " " * 7 + 'Nic nie znalazłem. [b]')
            time.sleep(2)

            print()
            print()

        @staticmethod
        def KeyErr(ke, pagename):
            print()
            glb().err(1, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")
            print(
                " " * 11 + "Hint:" + " " * 7 +
                str(ke).replace("'", '') if str(ke) != '0' else " " * 11 + "Hint:" +
                                                                " " * 7 + 'Nic nie znalazłem. [b]')
            time.sleep(2)
            print()
            print()

        @staticmethod
        def TooManyRowsErr(tmr, pagename):
            print()
            glb().err(2, 'Więcej niż 1 rząd w odebranych danych!', tmr=tmr, pgn=pagename)
            print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
            print()
            print(tmr, file=sys.stderr)
            tmr_database.append(tmr)
            time.sleep(2)
            print()
            print()

        @staticmethod
        def InvalidTitleErr():
            print()
            glb().err(3, "Podany tytuł jest nieprawidłowy.")
            time.sleep(2)
            print()
            print()

        @staticmethod
        def EmptyNameErr():
            print()
            glb().err(4, "Nie podano tytułu strony.")
            time.sleep(2)
            print()
            print()

        @staticmethod
        def KeyboardInterruptErr():
            print()
            glb().err(5, "Pomyślnie przerwano operację.")
            glb().output('Kontynuować? <T/N>')

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
