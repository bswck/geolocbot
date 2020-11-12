# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

from __init__ import geolocbotMain
from tasks_forwarder import geolocbotTask

geolocbotMain.intro()

while True:
    geolocbotTask.run()
