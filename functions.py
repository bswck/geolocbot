# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

import sys
from getcats import run
from databases import filtersimc, terencode, TooManyRows
from pywikibot import InvalidTitle


# Errors definitions.
class Error(Exception):
    """Base class for other exceptions"""
    pass


class EmptyNameError(Error):
    """Raised when no pagename has been provided"""
    pass


# Function checktitle checks if the providen title is valid.
def checktitle(pagename):
    try:

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
            print("Usunięto '" + pagename[:from2index] + "'.")

            st = str(pagename[from2index::])

        # .capitalize() changes further characters to lower,
        # that is why I use this method.
        # For example, if I used .capitalize(),
        # "ruciane-Nida" would be converted into "Ruciane-nida",
        # which is uncorrect.
        st = st[0].upper() + st[1::]

        # Return the corrected pagename string.
        return st

    except EmptyNameError:

        print("(nonsa.pl) Błąd: Nie podano tytułu strony.",
              file=sys.stderr)
        sys.exit()

    except ValueError:

        print("(nonsa.pl) Błąd: Strona '" + pagename + "' nie posiada odpowiednich kategorii lub nie istnieje.",
              file=sys.stderr)
        sys.exit()


# This runs the whole code.
def main(pagename):
    try:
        data = filtersimc(terencode(run(pagename)))

        # If even a name hasn't been captured,
        # that might mean the page doesn't exist.
        # The question is: "haven't you made a mistake whilst inputing?".
        if data.empty:
            raise ValueError('Czy nie popełniłeś błędu w nazwie strony?')

        # If no data, other than the name
        # hasn't been captured, that might mean
        # the article is not about a locality.
        elif data.columns.tolist() == ['NAZWA']:
            raise KeyError
        #
        # else:
        #     data = ask(data)

    except TypeError:
        print(
            "(nonsa.pl) [TypeError]: Ha!",
            file=sys.stderr)
        print(" " * 11 + "Hint: " + " " * 8 + str(TypeError))
        sys.exit()

    except ValueError as ve:
        print(
            "(nonsa.pl) [ValueError]: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.",
            file=sys.stderr)

        kropa = "" if str(ve)[-1] == "." or str(ve)[-1] == "?" or str(ve)[-1] == "!" else "."

        print(
            " " * 11 + "Hint: " + " " * 8 + str(ve) + kropa, file=sys.stderr)
        sys.exit()

    except KeyError:
        print(
            "(nonsa.pl) [KeyError]: Nie znaleziono odpowiednich kategorii lub strona '" + str(pagename) + "' nie istnieje.",
            file=sys.stderr)

        print(
            " " * 11 + "Hint:" + " " * 7 + "Czy nie popełniłeś błędu w nazwie strony?", file=sys.stderr)
        sys.exit()

    except TooManyRows as tmr:
        print("(nonsa.pl) [TooManyRows]: Więcej niż 1 rząd w odebranych danych!", file=sys.stderr)
        print(" " * 11 + "Wyjściowa baza:", file=sys.stderr)
        print()
        print(tmr, file=sys.stderr)
        sys.exit()

    except InvalidTitle as it:
        print("(nonsa.pl) [InvalidTitle]: Podany tytuł zawiera niedozwolone znaki.", file=sys.stderr)
        print(" " * 11 + "Hint:" + " " * 11 + str(it) + ".", file=sys.stderr)
        sys.exit()

    else:
        print(data)
        return data
