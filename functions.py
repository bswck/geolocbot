# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import sys
from getcats import run
from databases import filtersimc, terencode

class Error(Exception):
    """Base class for other exceptions"""
    pass

class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass

def checktitle(pagename):
    try:
        if len(pagename) == 0 or pagename == ' ' * len(pagename):
            raise EmptyNameError

        st = pagename[0].upper() + pagename[1::]

        if pagename.find(':') != -1:
            for i in pagename:

                if i == ':':
                    from2index = pagename.find(i) + 1

            # prints what has just been deleted (bot works only on the main namespace, sorry)
            print("Usunięto '" + pagename[:from2index] + "'.")
            st = str(pagename[from2index::])

        st = str(pagename)

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
        if data.empty == True:
            raise KeyError
    except TypeError:
        pass
    except KeyError:
        print(
            "(nonsa.pl) Błąd: Nie znaleziono rekordu w bazie danych.",
            file=sys.stderr)
        sys.exit()
    except ValueError as ve:
        print(
            "(nonsa.pl) Błąd: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.", file=sys.stderr)
        print(
            " " * 11 + "Hint: " + str(ve), file=sys.stderr)
        sys.exit()
    else:
        print(str(data))
