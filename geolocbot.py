# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

# just in case
import sys
import pywikibot as pwbot

# to measure the time spent on completing the function
import time

# importing needed definitions from other files in the repository
from getcats import run
from databases import filtersimc, terencode
from functions import checktitle, iserror

pagename = input('Podaj nazwę artykułu: ')
pagename = checktitle(pagename)

# 'start' time-measure
start = time.time()

data = filtersimc(terencode(iserror((run(pagename)), pagename)))

# 'stop' time-measure
end = time.time()

print(str(data))

print()

# prints the time spent on completing the function
print("Czas operacyjny: " + str(end - start).replace(".", ",") + "s.")
