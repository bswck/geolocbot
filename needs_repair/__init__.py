# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import pywikibot as pwbot
import traceback
import pandas
import sys
import time
from os import system, name


class geolocbotMain(object):
    def __init__(self):
        self.simc_database = pandas.read_csv("SIMC.csv",
                                             sep=';',
                                             usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'RM', 'MZ', 'NAZWA', 'SYM'])

        self.terc_database = pandas.read_csv("TERC.csv",
                                             sep=';',
                                             usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])

        self.input_prefix = '>b< '
        self.output_prefix = '[b] '
        self.exceptions_output_prefix = '(nonsa.pl) '
        self.history = []
        self.items_list_beginning = '<!-- początek listy -->\n'
        self.items_list_end = '<!-- koniec listy -->'
        self.site = pwbot.Site('pl', 'nonsensopedia')
        self.too_many_rows_inlist_database = []

    def too_many_rows_add(self, dataframe=''):
        """Saving TooManyRows to call it"""
        self.too_many_rows_inlist_database.append(dataframe)

    def too_many_rows_del(self):
        """Deleting TooManyRows DataFrame"""
        while self.too_many_rows_inlist_database:
            del self.too_many_rows_inlist_database[0]

    @staticmethod
    def clear():
        if name == 'nt':
            _ = system('cls')

        else:
            _ = system('clear')

    @staticmethod
    def end():
        """Closes the program"""
        geolocbotMain.output('Zapraszam ponownie!')
        print('---')
        exit()

    def delete_geoloc_template(self, pagename, reason):
        """Deleting template as an update procedure"""
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        page_to_delete_from = pwbot.Page(self.site, pagename)
        text_to_delete_from = page_to_delete_from.text

        if '{{lokalizacja' in text_to_delete_from:
            template = text_to_delete_from[text_to_delete_from.find('{{lokalizacja'):]
            template = template[:(template.find('}}') + 2)]
            page_to_delete_from.text = text_to_delete_from.replace(template, '')
            page_to_delete_from.save('/* aktualizacja */ usunięcie szablonu lokalizacja (' + str(reason) + ')')

    def input(self, input_message='Odpowiedź: '):
        """Geolocbot's specific input method"""
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        print()
        answer = input(self.input_prefix + input_message)
        self.history.append(answer)

        while answer == '' or answer == ' ' * len(answer):
            answer = input(self.input_prefix + input_message)

        if '*' in answer:
            if '*e' in answer and '*l' not in answer and '*debug_mode' not in answer:
                geolocbotMain.end()

            elif '*l' in answer and '*e' not in answer and '*debug_mode' not in answer:
                l_count = 0

                for l_index in range(len(self.history)):
                    if self.history[l_index] == '*l':
                        l_count += 1

                return geolocbotMain.goThroughList()

            elif '*debug_mode' in answer and '*e' not in answer:
                geolocbotMain.debug.output('Włączono tryb debugowania. Aby wyłączyć, uruchom program ponownie.')
                answer = geolocbotMain.input(input_message=input_message)

            elif len(answer) >= 2:
                if answer[answer.find('*') + 1] not in ['e', 'l'] and '*l' not in self.history:
                    geolocbotMain.output('Niepoprawna komenda.')
                    answer = geolocbotMain.input()

            else:
                geolocbotMain.output('Niepoprawna komenda.')
                answer = geolocbotMain.input()

        return answer

    def output(self, output_message):
        """Geolocbot's specific output method"""
        print(f'{self.output_prefix}{output_message}')

    def forward_error(self, error_type, output_error_message, hint='', page_title=False):
        """Function printing, recognising and differentiating errors"""
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        error = ['ValueError', 'KeyError', 'TooManyRows', 'InvalidTitle', 'EmptyNameError', 'KeyboardInterrupt']
        error_to_output = error[error_type] if isinstance(error_type, int) else error_type
        print(f'{self.exceptions_output_prefix}[{error_to_output}]: {output_error_message}', file=sys.stderr)

        if page_title is not False:
            # Error[2] is TooManyRows error
            if isinstance(error_type, int) and error[error_type] == error[2]:
                geolocbotMain.unhook(page_title, '([[Dyskusja użytkownika:Stim/TooManyRows-log|TooManyRows]])')

            else:
                geolocbotMain.unhook(page_title, (output_error_message if hint == '' else hint))
            geolocbotMain.delete_geoloc_template(page_title, output_error_message)

        if isinstance(error_type, int) and error[error_type] == error[2]:
            toomanyrows_database = self.too_many_rows_inlist_database[0]
            raw_name = str(toomanyrows_database.at[0, 'NAZWA'])
            page_name = f"'''[[{page_title}]]'''\n"
            report_page = pwbot.Page(self.site, 'Dyskusja użytkownika:Stim/TooManyRows-log')
            text = report_page.text

            if raw_name not in text:
                how_many_indexes = toomanyrows_database.shape[0]
                add = '\n\n\n<center>\n' + page_name + '{| class="wikitable sortable"\n|-\n! NAZWA !! SIMC\n|-'

                for index in range(how_many_indexes):
                    add = add + '\n| [[' + str(raw_name) + ']] || ' + str(toomanyrows_database.at[index, 'SYM']) + \
                          '\n|-'

                add = add + '\n|}\n~~~~~\n</center>'
                report_page.text = text + add
                report_page.save(u'/* raport */ TooManyRows: ' + str(raw_name))

            geolocbotMain.too_many_rows_del()

        if not isinstance(error_type, int):

            if str(error_type) not in error:
                report_page = pwbot.Page(self.site, 'Dyskusja użytkownika:Stim/geolocbot-bugs')
                text = report_page.text
                put_place = text.find('|}\n{{Stim}}')
                add = '| {{#vardefine:bugid|{{#expr:{{#var:bugid}} + 1}}}} {{#var:bugid}} || ' + \
                      str(error_type) + ' || <pre>' + str(traceback.format_exc()) + '</pre> || ~~~~~ || {{/p}}\n|-\n'
                report_page.text = text[:put_place] + add + text[put_place:]
                report_page.save(u'/* raport */ bugerror: ' + str(error_type))

    def list(self):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        page = pwbot.Page(self.site, 'Użytkownik:Stim/lista-wskazane')

        items_list = []
        items = page.text
        items = items[items.find(self.items_list_beginning) + len(self.items_list_beginning):]

        for character_index in range(len(items)):
            if items[character_index] == '*':
                if character_index != len(items):
                    item_row = items[character_index:]

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
                    item_row = items[character_index:]

                    if '{{/unhook' in item_row:
                        item_row = item_row[2:item_row.find(' {{/unhook')]

                    else:
                        item_row = item_row[2:items.find(self.items_list_end)]

                    if item_row[-1] == ' ':
                        item_row = item_row[:-1] + item_row[-1].replace(' ', '')

                    items_list.append(item_row.replace('[', '').replace(']', ''))

        geolocbotMain.debug.output(items_list) if len(items_list) <= 35 else None
        return items_list

    def unhook(self, pagename, information):
        geolocbotMain.debug.output(str(cast(types.FrameType, inspect.currentframe()).f_code.co_name))
        page = pwbot.Page(self.site, 'Użytkownik:Stim/lista')
        information = information.replace('{', '').replace('}', '')
        to_unhook = page.text

        if pagename in to_unhook:
            unhook_row = to_unhook[to_unhook.find(f'* [[{pagename}]]'):]
            unhook_row = unhook_row[:unhook_row.find('\n')]
            geolocbotMain.debug.output(unhook_row)

            if unhook_row == '':
                unhook_row = to_unhook[to_unhook.find(f'* [[{pagename}]] {{/unhook'):]
                unhook_row = unhook_row[:unhook_row.find('\n')]
                geolocbotMain.debug.output(unhook_row)

            if '{{/unhook' in unhook_row:
                geolocbotMain.debug.output(unhook_row)
                unhook_place = unhook_row.find(' {{/unhook|')
                unhook_put = unhook_row[unhook_place:unhook_row.find('}}')]
                geolocbotMain.debug.output(unhook_put)
                replaced_unhook = unhook_row.replace(unhook_put, ' {{/unhook|' + f'{information}')
                page.text = to_unhook.replace(unhook_row, replaced_unhook)

                if unhook_row != '':
                    page.save(f'/* -+{pagename} (nowy w miejsce starego) */ {information}')

                else:
                    raise geolocbotMain.exceptions.OutOfMemory('Coś w unhooku poważnie nie gra…')

            else:
                add = f'* [[{pagename}]] {{/unhook|{information}}}'
                page.text = to_unhook.replace(unhook_row, add)
                geolocbotMain.debug.output(unhook_row)
                geolocbotMain.debug.output(add)

                if unhook_row != '':
                    page.save(f'/* +{pagename} */ {information}')

                else:
                    raise geolocbotMain.exceptions.OutOfMemory('Coś w unhooku poważnie nie gra…')

    @staticmethod
    def intro():
        system('@echo off')
        geolocbotMain.clear()
        geolocbotMain.output('Witaj w programie Geolocbot 2020!')
        print()
        geolocbotMain.output('Ctrl + C przerywa wykonywanie operacji.')
        geolocbotMain.output('Wpisanie *e spowoduje zamknięcie programu.')
        geolocbotMain.output('Wpisanie *l spowoduje masowe przeoranie artykułów z listy na [[Użytkownik:Stim/lista]].')
        geolocbotMain.output('Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')

    class outputAndForward(object):
        """Class for processing errors"""
        @staticmethod
        def value_error(value_error_hint, pagename):
            print()
            geolocbotMain.forward_error(0,
                                        f"Nie znaleziono odpowiednich kategorii lub strona '{pagename}' nie istnieje.",
                                        hint=str(value_error_hint), page_title=pagename)
            time.sleep(2)

            print(
                " " * 11 + "Hint:" + " " * 9 +
                str(value_error_hint).replace("'", '')
                if str(value_error_hint) != '0'
                else " " * 11 + "Hint:" + " " * 7 + 'Nie odnaleziono informacji zgodnymi z kryteriami.'
            )
            time.sleep(2)

        @staticmethod
        def key_error(key_error_hint, pagename):
            print()
            key_error_hint_to_display = str(key_error_hint).replace("'", '') \
                if str(key_error_hint) != '0' \
                else 'Nie odnaleziono informacji w którejkolwiek z baz danych.'
            geolocbotMain.forward_error(1,
                                        f"Nie znaleziono odpowiednich kategorii lub strona '{pagename}' nie istnieje.",
                                        hint=key_error_hint_to_display, page_title=pagename)
            key_error_hint = " " * 12 + "Hint:" + " " * 7 + str(key_error_hint).replace("'", '') \
                if str(key_error_hint) != '0' \
                else " " * 12 + "Hint:" + " " * 7 + 'Niczego nie odnaleziono na podstawie kategorii.'
            print(key_error_hint)
            time.sleep(2)

        def too_many_rows_error(self, too_many_rows_database_hint, pagename):
            print()
            geolocbotMain.forward_error(2, 'Więcej niż 1 rząd w odebranych danych!', page_title=pagename)
            print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
            print()
            print(too_many_rows_database_hint, file=sys.stderr)
            self.too_many_rows_inlist_database.append(too_many_rows_database_hint)
            time.sleep(2)

        @staticmethod
        def invalid_title_error():
            print()
            geolocbotMain.forward_error(3, "Podany tytuł jest nieprawidłowy.")
            time.sleep(2)

        @staticmethod
        def keyboard_interrupt_error():
            print()
            geolocbotMain.forward_error(5, "Pomyślnie przerwano operację.")
            geolocbotMain.output('Kontynuować pracę programu? <T(ak)/N(ie)>')

    class debug(object):
        """Printing style for debugging purposes"""
        def __init__(self):
            self.debug_info = ''

        def output(self, output_message):
            self.debug_info = f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] funkcja/zmienna >> "
            if '*debug_mode' in geolocbotMain.history:
                geolocbotMain.output(f'{self.debug_info} {output_message}')

    class goThroughList(object):
        pass

    class notProvided(object):
        pass

    class exceptions(object):
        """Geolocbot's specific exceptions"""
        class geolocbotError(Exception):
            """Base class for Geolocbot exceptions"""
            pass

        class OutOfMemory(geolocbotError):
            """Raised when bot attempted to add too many bytes to a page"""
            pass

        class TooManyRows(geolocbotError):
            """Raised when too many rows appear in the table as an answer"""
            pass


geolocbotMain = geolocbotMain()
"""Base class for specific Geolocbot operations"""
geolocbotMain.debug = geolocbotMain.debug()
geolocbotMain.exceptions = geolocbotMain.exceptions()
geolocbotMain.outputAndForward = geolocbotMain.outputAndForward()
