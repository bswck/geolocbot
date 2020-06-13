# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.

# Import time to measure the time spent on completing the function.
import time
from functions import checktitle, main

# 'Start' time-measure.
start = time.time()

main()

# 'Stop' time-measure.
end = time.time()

print()

# Prints the time spent on completing the function.
print("Czas operacyjny: " + str(end - start)[:3].replace(".", ",") + "s.")
