# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia

import sys
import pywikibot as pwbot
import time
from getcats import run
from databases import terencode

def checktitle(pagename): # deleting annotations, adding exception etc.
    if pagename.find("Województwo") == -1:
        if len(pagename) != 0:
            if pagename.find(" (") != -1:
                for i in pagename:
                    if i == '(':
                        fromindex = pagename.find(i) - 1
                pagename = pagename.replace(pagename[fromindex::], '')
            pagename = pagename.capitalize()
            return pagename
        else:
            return pagename
    else:
        return pagename + " EXC"

pagename = input('Podaj nazwę artykułu: ')
pagename = checktitle(pagename)

def iserror(data, pagename):
    error = "<+Fiodorr> ERROR " + str(data) + "!"
    if data == 0:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie podano nazwy artykułu.", file=sys.stderr)
<<<<<<< HEAD
        return "<+Fiodorr> ERROR " + str(data) + "!"
    elif data == 1:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie znaleziono odpowiednich kategorii lub strona '" + pagename + "' nie istnieje.", file=sys.stderr)
        return "<+Fiodorr> ERROR " + str(data) + "!"
    elif data == 2:
        print("(nonsa.pl) Błąd " + str(data) + ": Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
        return "<+Fiodorr> ERROR " + str(data) + "!"
=======
        return error
    elif data == 1:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie znaleziono odpowiednich kategorii lub strona '" + pagename.replace(' EXC', '') + "' nie istnieje.", file=sys.stderr)
        print(" " * 19 + "Jeżeli podano nazwę przekierowania, proszę podać nazwę artykułu docelowego.", file=sys.stderr)
        print(" " * 19 + "Proszę również upewnić się, czy podana nazwa artykułu jest nazwą miejscowości.", file=sys.stderr)
        return error
    elif data == 2:
        print("(nonsa.pl) Błąd " + str(data) + ": Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
        return error
>>>>>>> master
    else:
        return data

start = time.time()
data = terencode(iserror((run(pagename)), pagename))
end = time.time()
print("✓ " + str(data))
print()
print("Czas operacyjny: " + str(end - start).replace(".", ",") + "s.")