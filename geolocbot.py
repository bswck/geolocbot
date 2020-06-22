# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from __init__ import geolocbot
from functions import checktitle, main, start

geolocbot.intro()

while True:
    main()

    # 'Stop' time-measure.
    end = time.time()

    print()

    # Prints the time spent on completing the function.
    time_taken = str(end - start[0]).replace(".", ",")
    before_comma = time_taken[:time_taken.find(',')]
    after_comma = time_taken[time_taken.find(',')::]
    time_to_print = before_comma + after_comma[:1]
    geolocbot.output("Czas operacyjny: " + time_to_print + "s.")
