# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Libraries and modules for Geoloc-Bot in one place. """

import abc
import pywikibot
import pywikibot.pagegenerators as pagegenerators
import logging
import warnings
import sys
import configparser
import os
import re
import pandas
import numpy
import inspect
import time
import better_abc
import types
import typing
import io
import requests

# for code completion
abc, pywikibot, logging, warnings, sys, configparser, os = abc, pywikibot, logging, warnings, sys, configparser, os
re, pandas, numpy, time, better_abc, requests, types = re, pandas, numpy, time, better_abc, requests, types
typing, inspect, pagegenerators, io, time = typing, inspect, pagegenerators, io, time

# pandas set-up
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 20)
pandas.set_option('display.width', 1000)

# other stuff
abstractClass, betterAbstractMetaclass = abc.ABC, better_abc.ABCMeta
abstractMethod, abstractAttribute = abc.abstractmethod, better_abc.abstract_attribute
nan = numpy.nan
