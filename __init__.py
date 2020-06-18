# -*- coding: utf-8 -*-
import pywikibot as pwbot
import traceback
import sys
import time
from os import system, name


# Errors definitions.
class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl


class glb(object):
    def __init__(self):
        self.i = '-b- '
        self.o = '[b] '
        self.n = '(nonsa.pl) '

    def clear(self):
        if name == 'nt':
            _ = system('cls')

        else:
            _ = system('clear')

    def end(self):
        geolocbot.output('Zapraszam ponownie!')
        print('---')
        exit()

    def input(self, input_message='Odpowiedź: ', cannot_be_empty=False):
        answer = input(str(self.i + input_message))

        if cannot_be_empty:
            if answer == '' or answer == ' ' * len(answer):
                raise EmptyNameError


        if answer[0] == '*':
            if '*e' in answer:
                glb().end()

            elif '*c' in answer and '*e' not in answer:
                glb().clear()
                glb().input(input_message)

            elif answer[1] not in ['c', 'e']:
                geolocbot.output('Niepoprawna komenda.')
                answer = geolocbot.input()

        return answer

    def output(self, output_message):
        print(self.o + output_message)

    def err(self, nmb, output_error_message):
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
        print(self.n + '[' + (error[nmb] if isinstance(nmb, int) else nmb) + ']: ' + output_error_message, file=sys.stderr)

        if not isinstance(nmb, int):

            if str(nmb) in bug_errors:
                report_page = pwbot.Page(site, 'Dyskusja użytkownika:Stim/geolocbot-bugs')
                text = report_page.text
                report_page.text = text + '\n----\nID = {{#vardefine:bugid|{{#expr:{{#var:bugid}} + 1}}}} {{#var:bugid}}\n\n' \
                              + str(traceback.format_exc()) + '~~~~~'
                report_page.save(u'/* raport */ bugerror: ' + str(nmb))

    def intro(self):
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

        def ValueErr(self, ve, pagename):
            print()
            glb().err(0, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")
            print(traceback.format_exc())
            time.sleep(2)

            print(
                " " * 11 + "Hint:" + " " * 9 +
                str(ve).replace("'", '') if str(ve) != '0' else " " * 11 + "Hint:" +
                                                                " " * 7 + 'Nic nie znalazłem. [b]')
            time.sleep(2)

            print()
            print()

        def KeyErr(self, ke, pagename):
            print()
            glb().err(1, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")
            print(traceback.format_exc())
            print(
                " " * 11 + "Hint:" + " " * 7 +
                str(ke).replace("'", '') if str(ke) != '0' else " " * 11 + "Hint:" +
                                                                " " * 7 + 'Nic nie znalazłem. [b]')
            time.sleep(2)
            print()
            print()

        def TooManyRowsErr(self, tmr):
            print()
            glb().err(2, 'Więcej niż 1 rząd w odebranych danych!')
            print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
            print()
            print(tmr, file=sys.stderr)
            time.sleep(2)
            print()
            print()

        def InvalidTitleErr(self, it):
            print()
            glb().err(4, "Podany tytuł jest nieprawidłowy.")
            time.sleep(2)
            print()
            print()

        def EmptyNameErr(self):
            print()
            glb().err(4, "Nie podano tytułu strony.")
            time.sleep(2)
            print()
            print()

        def KeyboardInterruptErr(self):
            print()
            glb().err(5, "Pomyślnie przerwano operację.")
            glb().output('Kontynuować? <T/N>')

geolocbot = glb()
geolocbot.exceptions = geolocbot.exceptions()
