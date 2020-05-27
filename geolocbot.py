# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia

import sys
import pywikibot as pwbot
from getcats import run
pagename = input('Podaj nazwę artykułu: ')

def iserror(data):
    if data == 0:
        print("Błąd 0: Zwrócona wartość jest równa początkowej.", file=sys.stderr)
    elif data == 1:
        print("Błąd 1: Zwrócona wartość jest pustym zbiorem.", file=sys.stderr)
    else:
        print(data)

data = (run(pagename))
iserror(data)


