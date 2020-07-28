# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

from __init__ import geolocbotMain
from needs_repair.tasks_forwarder import geolocbotTask

geolocbotMain.intro()

while True:
    geolocbotTask.run()
