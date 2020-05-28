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
    if data == 0:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie podano nazwy artykułu.", file=sys.stderr)
        return "< Fiodorr> ERROR " + str(data) + "!"
    elif data == 1:
        print("(nonsa.pl) Błąd " + str(data) + ": Nie znaleziono odpowiednich kategorii lub strona '" + pagename + "' nie istnieje.", file=sys.stderr)
        return "< Fiodorr> ERROR " + str(data) + "!"
    elif data == 2:
        print("(nonsa.pl) Błąd " + str(data) + ": Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
        return "< Fiodorr> ERROR " + str(data) + "!"
    else:
        return data

start = time.time()
data = terencode(iserror((run(pagename)), pagename))
end = time.time()
print("✓ " + str(data))
print()
print("<+Fiodorr> ale wolno, " + str(end - start) + "s.")

