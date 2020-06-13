# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import sys
import time
from getcats import run
from databases import filtersimc, terencode, TooManyRows
from pywikibot import InvalidTitle
from querying import coords, getqid


# Errors definitions.
class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass


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
        print("[bot] Usunięto '" + pagename[:from2index] + "'.")

        st = str(pagename[from2index::])
        checktitle(st)

    if " (" in pagename:
        for i in pagename:

            if i == '(':
                fromindex = pagename.find(i) - 1
                print("[bot] Usunięto dopisek '" + pagename[fromindex + 1:] + "'.")

    # .capitalize() changes further characters to lower,
    # that is why I use this method.
    # For example, if I used .capitalize(),
    # "ruciane-Nida" would be converted into "Ruciane-nida",
    # which is uncorrect.
    st = st[0].upper() + st[1::]

    # Return the corrected pagename string.
    return st


def exit():
    print('[bot] Zapraszam ponownie!')
    print('***')
    sys.exit()


# This runs the whole code.
def main():
    try:
        pagename = input('-bot- Podaj nazwę artykułu: ')

        exit() if '*e' in pagename else None

        pagename = checktitle(pagename)
        data = filtersimc(terencode(run(pagename)))

        # The question is: "haven't you made a mistake whilst inputing?".
        if data is None:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

        else:
            data = coords(getqid(data))

    # except TypeError:
    #     print(
    #         "(nonsa.pl) [TypeError]: Ha!",
    #         file=sys.stderr)
    #     print(" " * 11 + "Hint: " + " " * 8 + str(TypeError))
    #     print()
    #     print()
    #     main()

    except ValueError as ve:
        print(
            "(nonsa.pl) [ValueError]: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie "
                                                                                                            "istnieje.",
            file=sys.stderr)

        kropa = "" if str(ve)[-1] == "." or str(ve)[-1] == "?" or str(ve)[-1] == "!" else "."

        print(
            " " * 11 + "Hint: " + " " * 8 + str(ve) + kropa, file=sys.stderr)
        time.sleep(2)
        print()
        print()
        main()

    # except KeyError as ke:
    #     print(
    #         "(nonsa.pl) [KeyError]: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie "
    #                                                                                                       "istnieje.",
    #         file=sys.stderr)
    #
    #     print(
    #         " " * 11 + "Hint:" + " " * 7 + str(ke).replace("'", '') if str(ke) != '0' else " " * 11 + "Hint:" + " " * 7 + 'Nic nie znalazłem. [bot]', file=sys.stderr)
    #     time.sleep(2)
    #     print()
    #     print()
    #     main()

    except TooManyRows as tmr:
        print("(nonsa.pl) [TooManyRows]: Więcej niż 1 rząd w odebranych danych!", file=sys.stderr)
        print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
        print()
        print(tmr, file=sys.stderr)
        time.sleep(2)
        print()
        print()
        main()

    except InvalidTitle as it:
        print("(nonsa.pl) [InvalidTitle]: Podany tytuł jest nieprawidłowy.", file=sys.stderr)
        print(" " * 11 + "Hint:" + " " * 11 + str(it) + ".", file=sys.stderr)
        time.sleep(2)
        print()
        print()
        main()

    except EmptyNameError:

        print("(nonsa.pl) Błąd: Nie podano tytułu strony.",
              file=sys.stderr)
        time.sleep(2)
        print()
        print()
        main()

    except KeyboardInterrupt:
        print("(nonsa.pl) [KeyboardInterrupt]: Pomyślnie przerwano operację.", file=sys.stderr)
        print('-bot- Kontynuować? <T/N>')
        ct = str(input('Odpowiedź: ')).upper()
        ans = ['T', 'N']

        while ct not in ans:
            ct = str(input('Odpowiedź <T/N>: ')).upper()

        if ct == 'T':
            print()
            print()
            main()

        else:
            exit()

    else:
        print(data)
        return data
