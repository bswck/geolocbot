# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from __init__ import geolocbotMain
from tasks_forwarder import geolocbotTask

geolocbotMain.intro()

while True:
    geolocbotTask.run()

    # 'Stop' time-measure.
    end = time.time()

    print()

    # Prints the time spent on completing the function.
    time_taken = (end - geolocbotTask.start[0])
    time_to_print = "%.1f" % time_taken
    geolocbotMain.output("Czas operacyjny: " + str(time_to_print).replace('.', ',') + "s.")
