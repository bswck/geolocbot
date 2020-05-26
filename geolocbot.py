# -*- coding: utf-8 -*-
# Author: Stim, 2020
# Geolocalisation bot for Nonsensopedia

import pywikibot as pwbot
from getcats import run
pagename = input('Podaj nazwę artykułu: ')

data = (run(pagename))
print(data)
