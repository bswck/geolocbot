from __future__ import annotations

import collections
import itertools
import operator
import typing

import pywikibot
from pywikibot import pagegenerators

if typing.TYPE_CHECKING:
    from geolocbot.teryt import TERYT

WikidataLocation = collections.namedtuple("WikidataLocation", "lat lon wikidata")


class WikidataLocationSearch:
    QUERY_TEMPLATE: str = """
    SELECT ?coord ?item ?itemLabel
    WHERE
    {
      ?item wdt:%(prop)s '%(key)s'.
      OPTIONAL {?item wdt:P625 ?coord}.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
    }
    """
    COORD_PROPERTY: str = "P625"  # 3.12.2020
    SIMC_PROPERTY: str = "P4046"  # 3.12.2020
    TERC_PROPERTY: str = "P1653"  # 3.12.2020
    NTS_PROPERTY: str = "P1653"  # 3.12.2020
    HIERARCHY: tuple[str, str, str] = ("SIMC", "TERC", "NTS")

    def __init__(self, site: pywikibot.APISite | None = None) -> None:
        if site is None:
            site = pywikibot.Site("wikidata", "wikidata")
        self.site = site

    def query(self, prop: str, key: str) -> pywikibot.ItemPage:
        """
        Query Wikidata for an item with some certain SIMC or TERC property value.
        Takes prop (P4046 if SIMC or P1653 if TERC) and key (value of the property).
        """
        query = self.QUERY_TEMPLATE % {"prop": prop, "key": key}
        generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=self.site)
        result = list(itertools.islice(generator, 1))
        return result[0] if result else None

    def search(self, teryt: TERYT) -> WikidataLocation:
        """Search for the location of a locality, basing on the provided TERYT data."""
        page = result = None
        memo = {}
        items = sorted(
            filter(operator.attrgetter("sub"), teryt[1:]),
            key=lambda i: self.HIERARCHY.index(i.registry_name),
        )
        for primary in (1, 0):
            for item in items:
                prop = item.wd_prop
                key = item.get_wd_key(primary)
                if memo.get(prop) == key:
                    continue
                memo[prop] = key
                page = self.query(item.wd_prop, item.get_wd_key(primary))
                result = self._parse_result(page, teryt) or result
                if result and result.lat:
                    break
            result = self._parse_result(page, teryt) or result
            if result and result.lat:
                break
        return result

    def _parse_result(
        self, result: pywikibot.ItemPage, teryt: TERYT
    ) -> WikidataLocation:
        location = None
        if result:
            source = result.get()
            for label in source["labels"].values():
                label = label.lower().strip()
                if label in (teryt.sub.name.lower(), teryt.sub.page_name.lower()):
                    prop = result.claims.get(self.COORD_PROPERTY)
                    if prop:
                        coords = prop[0].getTarget()
                        lat = coords.lat
                        lon = coords.lon
                    else:
                        lat = lon = None
                    location = WikidataLocation(
                        lat=lat, lon=lon, wikidata=result.title()
                    )
        return location
