# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia
# License: GNU GPLv3

# to measure the time spent on completing the function
import time

from functions import checktitle, main

pagename = input('Podaj nazwę artykułu: ')
pagename = checktitle(pagename)

# 'start' time-measure
start = time.time()

main(pagename)

# 'stop' time-measure
end = time.time()

print()

# prints the time spent on completing the function
print("Czas operacyjny: " + str(end - start).replace(".", ",") + "s.")
