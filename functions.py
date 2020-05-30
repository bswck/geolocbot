# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

import sys

# deleting annotations, adding exception etc.
def checktitle(pagename):

    if pagename.find("Województwo") != -1:
        return pagename + " EXC"

    elif len(pagename) == 0:
        return 0

    elif pagename.find(":") != -1:
        for i in pagename:

            if i == ':':
                from2index = pagename.find(i) + 1

        # prints what has just been deleted (bot works only on the main namespace, sorry)
        print("Usunięto '" + pagename[:from2index] + "'.")
        return str(pagename[from2index::]).capitalize()
    else:
        return str(pagename).capitalize()

# checks if data isn't an error value (0, 1, 2)
# TO DO: Make exceptions from these
def iserror(data, pagename):
    error = "<+Fiodorr> ERROR " + str(data) + "!"

    if data == 0:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie podano nazwy artykułu.", file=sys.stderr)
        return error

    elif data == 1:
        print(
            "(nonsa.pl) Błąd " + str(data) + ": Nie znaleziono odpowiednich kategorii lub strona '" + pagename.replace(
                ' EXC', '') + "' nie istnieje.", file=sys.stderr)
        print(" " * 19 + "Jeżeli podano nazwę przekierowania, proszę podać nazwę artykułu docelowego.", file=sys.stderr)
        print(" " * 19 + "Proszę również upewnić się, czy podana nazwa artykułu jest nazwą miejscowości.",
              file=sys.stderr)
        return error

    elif data == 2:
        print("(nonsa.pl) Błąd " + str(data) + ": Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
        return error

    else:
        return data
