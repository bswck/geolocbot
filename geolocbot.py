# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from functions import checktitle, main, start

print("""
[b] _________          ______           ______       _____ 
[b] __  ____/_____________  /______________  /_________  /_
[b] _  / __ _  _ \  __ \_  /_  __ \  ___/_  __ \  __ \  __/
[b] / /_/ / /  __/ /_/ /  / / /_/ / /__ _  /_/ / /_/ / /_  
[b] \____/  \___/\____//_/  \____/\___/ /_.___/\____/\__/  

[b]                                         Geolocbot 2020
        """)

print()
print('[b] Ctrl + C przerywa wykonywanie operacji.')
print('[b] Wpisanie *e spowoduje zamknięcie programu.')
print('[b] Ja na gitlabie: https://gitlab.com/nonsensopedia/bots/geolocbot.')
print()

while True:
    main()

    # 'Stop' time-measure.
    end = time.time()

    print()

    # Prints the time spent on completing the function.
    print("[b] Czas operacyjny: " + str(end - start[0])[:5].replace(".", ",") + "s.")
