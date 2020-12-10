# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Libraries and modules for Geoloc-Bot in one place. """

import abc
import os
import sys
import pathlib
try:
    import pywikibot
except ImportError:
    sys.path.extend([str(pathlib.Path(os.getcwd()).parent)])
    import pywikibot

try:
    import pywikibot.pagegenerators as pagegenerators
except ImportError:
    from pywikibot import pagegenerators
import logging
import warnings
import configparser
import re
import pandas
import numpy
import inspect
import time
import datetime
import better_abc
import types
import typing
import io
import requests

# for code completion
abc, pywikibot, logging, warnings, sys, configparser, os = abc, pywikibot, logging, warnings, sys, configparser, os
re, pandas, numpy, time, better_abc, requests, types = re, pandas, numpy, time, better_abc, requests, types
typing, inspect, pagegenerators, io, time, datetime = typing, inspect, pagegenerators, io, time, datetime

# pandas setup
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)

# other stuff
ABC, bABCMeta = abc.ABC, better_abc.ABCMeta
abstractmethod, abstractattribute = abc.abstractmethod, better_abc.abstract_attribute
nan = numpy.nan
