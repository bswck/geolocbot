# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia

import sys
import pywikibot as pwbot
import time
from getcats import run
from databases import terencode
from functions import checktitle, iserror

pagename = input('Podaj nazwę artykułu: ')
pagename = checktitle(pagename)

start = time.time()
data = terencode(iserror((run(pagename)), pagename))
end = time.time()
print("✓ " + str(data))
print()
print("Czas operacyjny: " + str(end - start).replace(".", ",") + "s.")