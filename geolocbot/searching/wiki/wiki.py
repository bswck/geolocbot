# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.utils import *
from geolocbot.libs import *
from geolocbot.prepare import *
import geolocbot.searching.teryt as teryt


__all__ = ('WikiWrapper',)

_botconf = bot_config()


class BotSite:
    def __init__(self, site: pywikibot.Site):
        self.site = site
        self.processed_page = pywikibot.Page(self.site, 'Main Page')  # default


def _wpage(title):
    return pywikibot.Page(source=WikiWrapper().site, title=title)


def _clear_title(page):
    return page.title(with_section=False, underscore=False, without_brackets=True)


# = WIKIDATA ===========================================================================================================
# To do: replace NTS IDs from 2005 confused with TERC IDs (which is called "TERYT" municipality code) with proper,
# up to date TERC IDs.
#
# See: https://www.wikidata.org/wiki/Property:P1653

wdt_coord_property = 'P625'  # .................... 3.12.2020
wdt_simc_property = 'P4046'  # .................... 3.12.2020
wdt_terc_property = 'P1653'  # .................... 3.12.2020
wtd_nts_property = 'P1653'  # ..................... 3.12.2020


class WikidataWrapper(BotSite):
    def __init__(self):
        super(WikidataWrapper, self).__init__(
            site=pywikibot.Site('wikidata', 'wikidata', user=_botconf['wikidata-user'])
        )
        self.processed_item = None
        self.nil = None

    class GeolocQueries:
        def __init__(self, simc, terc='', nts=''):
            self.simc = simc
            self.terc, self.nts = terc, nts
            self.sparql = \
                f"""
                SELECT ?coord ?item ?itemLabel 
                WHERE
                {"{"}
                  ?item wdt:%(prop)s '%(terid)s'.
                  OPTIONAL {"{"}?item wdt:{wdt_coord_property} ?coord{"}"}.
                  SERVICE wikibase:label {"{"} bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". {"}"}
                {"}"}
                """

        @typecheck
        def construct_query(self, subsystem: str):
            propname = 'wdt_' + subsystem.lower() + '_property'
            __assert(propname in globals(), f'{propname} is not defined')
            prop = eval(propname)
            __assert(prop, f'cannot construct a query: {subsystem} ID has not been provided')
            terid = getattr(self, subsystem.lower())
            return self.sparql % dict(prop=prop, terid=terid)

    @typecheck
    def query(self, query, maximum: int = 1, index=None):
        """
        Send a SPARQL query to Wikidata Query Service.

        Parameters
        ----------
        query : str
            Query to be sent, in SPARQL.
        maximum: int
            Maximum number of results.
        index: int or type(None)
            Results tuple indice to return. If not specified, returns all results.
        """
        result = tuple(pagegenerators.WikidataSPARQLPageGenerator(query, site=self.site))
        __assert(len(result) <= maximum, f'got {len(result)} results whilst maximum was set to {maximum}')
        return result[index] if isinstance(index, int) else result

    @typecheck
    def _get_wdtitem(self, *, simc: str, terc: str = '', nts: str = ''):
        geolocqueries = self.GeolocQueries(simc=simc, terc=terc, nts=nts)
        results = {}
        for subsystem in teryt.subsystems:
            if eval(subsystem):
                results |= {subsystem: self.query(query=geolocqueries.construct_query(subsystem=subsystem), index=0)}
        for result in results.values():
            if result:
                self.processed_item = result
                return self.processed_item

        __assert(not isinstance(self.nil, type(None)), ValueError(
            f'Wikidata ItemPage not found: '
            f'{representation("WikidataQuery-%r" % self.processed_page, simc=simc, terc=terc, nts=nts)}'
        ))
        return self.nil

    @typecheck
    def _get_wdtitem_source(self, item: pywikibot.ItemPage):
        """
        Get the Wikidata item source.

        Parameters
        ----------
        item: pywikibot.ItemPage
            Item to get.

        Returns
        -------
        TODO: name the rtype
            Source data of the item.
        """
        try:
            return item.get()
        except pywikibot.exceptions.MaxlagTimeoutError:  # shit happens
            self._get_wdtitem_source(item=item)

    @typecheck
    def _get_wdtitem_property(self, item: pywikibot.ItemPage, _property):
        source = self._get_wdtitem_source(item)
        labels = values_(dict(source['labels']))
        name = _clear_title(self.processed_page)
        __assert(any(xcl(x=name, seq=labels)), f'no item label {item} matches pagename {self.processed_page.title()}')
        if _property not in item.claims:
            return ()
        return item.claims[_property]

    @typecheck
    def _get_wdtitem_coords(self, item: pywikibot.ItemPage):
        coords = self._get_wdtitem_property(item, wdt_coord_property)[0].getTarget()
        return {'lat': coords.lat, 'lon': coords.lon, 'source': self.processed_item}

    @getpagebyname
    def geolocate(self, _pagename, *, simc: str, terc: str = '', nts: str = '', nil=None):
        self.nil = nil
        wdt_item = self._get_wdtitem(simc=simc, terc=terc, nts=nts)
        if wdt_item:
            return self._get_wdtitem_coords(item=wdt_item)
        return wdt_item
# ======================================================================================================================


# = WIKI ===============================================================================================================
class WikiWrapper(BotSite):
    def __init__(self):
        super(WikiWrapper, self).__init__(site=pywikibot.Site('pl', 'nonsensopedia', user=_botconf['user']))
        self.base = WikidataWrapper()
        self.page_terinfo = {}
        self.ter_cat_prefixes = {
            'Kategoria:Województwo ': 'voivodship', 'Kategoria:Powiat ': 'powiat', 'Kategoria:Gmina ': 'gmina'
        }
        self.indirect_ter_cat_prefixes = ('Kategoria:Powiaty w', 'Kategoria:Gminy w', 'Kategoria:Województwa w')
        self.trace = []
        self.doubling = []

    @staticmethod
    def _index_prefix(wikitext: str, prefix='[[Kategoria:'):
        wikitext, lower_prefix = wikitext.lower(), prefix.lower()
        return wikitext.index(lower_prefix) if lower_prefix in wikitext else len(wikitext)

    @staticmethod
    def _insert_to_wikitext(wikitext: str, index: int, newtext: str):
        remaining = wikitext[index:] if index <= len(wikitext) - 1 else ''
        return f'{wikitext[:index]}\n{newtext}\n{remaining}'

    def _get_section_name(self): pass

    @getpagebyname
    @typecheck
    def insert(self, _pagename, template):
        wikitext: str = self.processed_page.text
        index = self._index_prefix(wikitext=wikitext)
        self.processed_page.text = self._insert_to_wikitext(wikitext=wikitext, index=index, newtext=template)
        self.processed_page.save()

    @getpagebyname
    @typecheck
    def loc_terinfo(self, _pagename: str, nil=None):
        def look_up(master: str) -> "dict":
            self.trace.append(master)
            if master not in self.doubling:
                subcategories = \
                    [subcat.title() for subcat in _wpage(master).categories() if 'hidden' not in subcat.categoryinfo]
                find(subcategories=subcategories, master=master)
            return self.page_terinfo

        def find(master: str, subcategories: list):
            if master in self.trace and all(xcl(seq=self.indirect_ter_cat_prefixes, x=master, _xcl=False)):
                self.doubling.append(master)
            [pull_data(sub) if ter_prefix(sub) else look_up(sub) for sub in subcategories]

        def pull_data(subcat: str):
            self.page_terinfo[self.ter_cat_prefixes[ter_prefix(subcat)]] = subcat.split(ter_prefix(subcat))[1]

        def ter_prefix(subcat: str):
            return next(iter([cat_prefix for cat_prefix in self.ter_cat_prefixes if cat_prefix in subcat]), False)

        def fillempty(data: dict):
            simc = teryt.SIMC()
            hierarchy = tuple(simc.loctype_nim.keys())
            for loctype in hierarchy:
                origin = simc.search(**data, loctype=loctype)
                if origin.parsed:
                    origin.transfer('nts') if origin.transfer('terc').parsed else do_nothing()
                    return origin
            __assert(not isinstance(nil, type(None)), 'Item not found in TERYT register')
            return nil

        self.page_terinfo['name'] = _clear_title(self.processed_page)
        return fillempty(look_up(self.processed_page.title()))

# ======================================================================================================================
