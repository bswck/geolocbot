# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Libraries and modules for Geoloc-Bot in one place. """

import abc
import pywikibot
import logging
import warnings
import sys
import configparser
import os
import re
import pandas
import numpy
import time
import better_abc
import requests

# for code completion
abc, pywikibot, logging, warnings, sys, configparser, os = abc, pywikibot, logging, warnings, sys, configparser, os
re, pandas, numpy, time, better_abc, requests = re, pandas, numpy, time, better_abc, requests
