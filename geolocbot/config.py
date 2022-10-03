"""
This module contains the configuration layer for the bot.
It's responsible for loading the configuration from the environment and providing it to the bot.
"""

from __future__ import annotations

import os
import configparser
import sys

import pywikibot.config

try:
    import dotenv
except ImportError:
    dotenv = None  # pragma: nocover

if dotenv:
    dotenv.load_dotenv()

WIKI_LOGIN: str | None = os.getenv("WIKI_LOGIN")
WIKIDATA_LOGIN: str | None = os.getenv("WIKIDATA_LOGIN", WIKI_LOGIN)

pywikibot.config.usernames["wikidata"]["wikidata"] = WIKIDATA_LOGIN
pywikibot.config.usernames["*"]["*"] = WIKI_LOGIN

config: configparser.ConfigParser = configparser.ConfigParser()

VERBOSE: bool = "-verbose" in sys.argv or "-v" in sys.argv
CONFIG_FILENAME: str = os.getenv("CONFIG_FILE", "geolocbot.conf")
config.read(CONFIG_FILENAME, encoding="UTF-8")

TEMPLATE_NAME: str = config.get("template", "name")
REPLACE_TEMPLATE_NAME: str = config.get("template", "replace_template")
PARAM_METADATA: dict[str, str] = dict(
    location=config.get("template", "location_param", fallback="location"),
    wikidata=config.get("template", "wikidata_param", fallback="wikidata"),
    terc=config.get("template", "terc_param", fallback="terc"),
    simc=config.get("template", "simc_param", fallback="simc"),
)
GENERATOR_CATEGORY: str = config.get("geolocbot", "generator_category")
SUMMARY_TEMPLATE: str = config.get(
    "geolocbot", "summary_template", fallback="Geolocbot: $page_name"
)


pywikibot.config.family_files["dane"] = "https://dane.nonsa.pl/api.php"


class Nonsensopedia(pywikibot.Family):
    name: str = "nonsensopedia"
    langs: dict[str, str] = {
        "pl": "nonsa.pl",
        "ar": "beidipedia.miraheze.org",
        "cs": "necyklopedie.org",
        "da": "spademanns.fandom.com",
        "de": "de.uncyclopedia.co",
        "en": "en.uncyclopedia.co",
        "en-gb": "uncyclopedia.ca",
        "es": "inciclopedia.org",
        "fr": "desencyclopedie.org",
        "he": "eincyclopedia.org",
        "it": "nonciclopedia.org",
        "nap": "en.uncyclopedia.co",
        "olb": "absurdopedia.wiki",
        "ru": "absurdopedia.net",
        "vi": "uncyclopedia.ca",
        "zh": "uncyclopedia.miraheze.org",
    }
    script_paths: dict[str, str] = {
        "pl": "",
        "ar": "/w",
        "cs": "/w",
        "da": "",
        "de": "/w",
        "en": "/w",
        "en-gb": "/w",
        "es": "/w",
        "fr": "/w",
        "he": "/w",
        "it": "/w",
        "nap": "/w",
        "olb": "/w",
        "ru": "/w",
        "vi": "/w",
        "zh": "/w",
    }
    protocols: dict[str, str] = {
        "pl": "https",
        "ar": "https",
        "cs": "https",
        "da": "https",
        "de": "https",
        "en": "https",
        "en-gb": "https",
        "es": "https",
        "fr": "https",
        "he": "https",
        "it": "https",
        "nap": "https",
        "olb": "https",
        "ru": "https",
        "vi": "https",
        "zh": "https",
    }

    def eventstreams_path(self, code: str) -> None:
        raise NotImplementedError("This family does not support EventStreams")

    def eventstreams_host(self, code: str) -> None:
        raise NotImplementedError("This family does not support EventStreams")

    def scriptpath(self, code: str) -> str:
        return self.script_paths[code]

    def protocol(self, code: str) -> str:
        return self.protocols[code]


FAMILY: pywikibot.Family = Nonsensopedia()
