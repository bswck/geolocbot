# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from __init__ import geolocbot
from functions import main, start

geolocbot.intro()

while True:
    main()

    # 'Stop' time-measure.
    end = time.time()

    print()

    # Prints the time spent on completing the function.
    time_taken = (end - start[0])
    time_to_print = "%.1f" % time_taken
    geolocbot.output("Czas operacyjny: " + str(time_to_print).replace('.', ',') + "s.")
