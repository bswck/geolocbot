# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from functions import checktitle, main

print("""
_________          ______           ______       _____ 
__  ____/_____________  /______________  /_________  /_
_  / __ _  _ \  __ \_  /_  __ \  ___/_  __ \  __ \  __/
/ /_/ / /  __/ /_/ /  / / /_/ / /__ _  /_/ / /_/ / /_  
\____/  \___/\____//_/  \____/\___/ /_.___/\____/\__/  

                                         Geolocbot 2020
        """)

print()
print('[bot] Ctrl + C przerywa wykonywanie operacji.')
print('[bot] Wpisanie *e spowoduje zamknięcie programu.')
print('[bot] Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')
print()

# 'Start' time-measure.
start = time.time()

main()

# 'Stop' time-measure.
end = time.time()

print()

# Prints the time spent on completing the function.
print("Czas operacyjny: " + str(end - start)[:3].replace(".", ",") + "s.")
