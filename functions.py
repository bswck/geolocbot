# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import sys
from getcats import run
from databases import filtersimc, terencode, TooManyRows
from errors import EmptyNameError
from pywikibot import InvalidTitle

def checktitle(pagename):
    global from2index
    try:

        if len(pagename) == 0 or pagename == ' ' * len(pagename):
            raise EmptyNameError

        st = pagename

        if pagename.find(':') != -1:
            for i in pagename:

                if i == ':':
                    from2index = pagename.find(i) + 1

            # prints what has just been deleted (bot works only on the main namespace, sorry)
            print("Usunięto '" + pagename[:from2index] + "'.")

            st = str(pagename[from2index::])

        # .capitalize() changes further characters to lower
        st = st[0].upper() + st[1::]

        return st

    except EmptyNameError:

        print("(nonsa.pl) Błąd: Nie podano tytułu strony.",
              file=sys.stderr)
        sys.exit()

    except ValueError:

        print("(nonsa.pl) Błąd: Strona '" + pagename + "' nie posiada odpowiednich kategorii lub nie istnieje.",
              file=sys.stderr)
        sys.exit()


def main(pagename):
    try:
        data = filtersimc(terencode(run(pagename)))

        if data.empty:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')
        elif data.columns.tolist() == ['NAZWA']:
            raise KeyError

    except TypeError:
        pass

    except KeyError:
        print(
            "(nonsa.pl) Błąd: Nie znaleziono rekordu w bazie danych odpowiadającego zapytaniu '" + pagename + "'.",
            file=sys.stderr)
        sys.exit()

    except ValueError as ve:
        print(
            "(nonsa.pl) Błąd: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.",
            file=sys.stderr)

        kropa = "" if str(ve)[-1] == "." else "."

        print(
            " " * 11 + "Hint: " + str(ve) + kropa, file=sys.stderr)
        sys.exit()

    except TooManyRows as tmr:
        print("(nonsa.pl) Błąd: Więcej niż 1 rząd w odebranych danych!", file=sys.stderr)
        print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
        print()
        print(tmr, file=sys.stderr)
        sys.exit()

    except InvalidTitle as it:
        print("(nonsa.pl) Błąd: Podany tytuł zawiera niedozwolone znaki.", file=sys.stderr)
        print(" " * 11 + "Hint: " + str(it) + ".", file=sys.stderr)
        sys.exit()

    else:
        print(data)
