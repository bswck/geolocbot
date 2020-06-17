# -*- coding: utf-8 -*-
import pywikibot as pwbot
import traceback
import sys
import time

site = pwbot.Site('pl', 'nonsensopedia')  # we're on nonsa.pl
report_page = pwbot.Page(site, 'Dyskusja użytkownika:Stim/geolocbot-bugs')

class glb(object):
    def __init__(self):
        self.i = '-b- '
        self.o = '[b] '
        self.n = '(nonsa.pl) '

    def input(self, input_message='Odpowiedź: '):
        answer = input(str(self.i + input_message))
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
                      'OverflowError',
                      'SyntaxError',
                      'TabError',
                      'UnboundLocalError']
        print(self.n + '[' + (error[nmb] if isinstance(nmb, int) else nmb) + ']: ' + output_error_message, file=sys.stderr)

        if not isinstance(nmb, int):

            if str(nmb) in bug_errors:
                text = report_page.text
                report_page = text + '\n----\nID = {{#vardefine:bugid|{{#expr:{{#var:bugid}} + 1}}}} {{#var:bugid}}}\n' \
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
        glb().output('Wpisanie *e spowoduje zamknięcie programu.')
        glb().output('Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')
        print()

    class exceptions(object):

        def ValueErr(self, pagename):
            glb().err(0, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")
            time.sleep(2)
            print()
            print()

        def KeyErr(self, ke, pagename):
            print()
            glb().err(1, "Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.")

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
            glb().err(4, "[InvalidTitle]: Podany tytuł jest nieprawidłowy.")
            time.sleep(2)
            print()
            print()

        def EmptyNameErr(self):
            print()
            glb().err(4, "Błąd: Nie podano tytułu strony.")
            time.sleep(2)
            print()
            print()

        def KeyboardInterruptErr(self):
            print()
            glb().err(5, "(nonsa.pl) [KeyboardInterrupt]: Pomyślnie przerwano operację.")
            print('-b- Kontynuować? <T/N>')

geolocbot = glb()
geolocbot.exceptions = geolocbot.exceptions()