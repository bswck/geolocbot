# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia

import sys
import pywikibot as pwbot
import time
from getcats import run
from databases import terencode

pagename = input('Podaj nazwę artykułu: ')
if len(pagename) != 0:
    pagename = pagename[0].upper() + pagename[1::] # capitalize first letter

def iserror(data, pagename):
    error = "<+Fiodorr> ERROR " + str(data) + "!"
    if data == 0:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie podano nazwy artykułu.", file=sys.stderr)
        return error
    elif data == 1:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie znaleziono odpowiednich kategorii lub strona '" + pagename + "' nie istnieje.", file=sys.stderr)
        print("                   Jeżeli podano nazwę przekierowania, proszę podać nazwę artykułu docelowego.", file=sys.stderr)
        return error
    elif data == 2:
        print("(nonsa.pl) Błąd " + str(data) + ": Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
        return error
    else:
        return data

start = time.time()
data = terencode(iserror((run(pagename)), pagename))
end = time.time()
print("✓ " + str(data))
print()
print("<+Fiodorr> serio? " + str(end - start).replace(".", ",") + "s.")

