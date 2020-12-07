# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.utils import *
from geolocbot.exceptions import *
from geolocbot.libs import *
from geolocbot.loaders import *
import geolocbot.searching.teryt as teryt


__all__ = ('Wiki',)

_botconf = fetch_bot_config()


class BotSite:
    def __init__(self, site: pywikibot.Site):
        self.site = site
        self.processed_page = pywikibot.Page(self.site, 'Main Page')  # default


def _wpage(title):
    return pywikibot.Page(source=wiki.site, title=title)


coord_property = 'P625'
# To do in Wikidata: replace NTS IDs from 2005 confused with TERC IDs (which is called "TERYT" municipality code)
# with proper, up to date TERC IDs.
#
# See: https://www.wikidata.org/wiki/Property:P1653
# ==================================================================================================
wdt_simc_property = 'P4046'  # ............................................................. 3.12.2020 .
wdt_terc_property = 'P1653'  # ............................................................. 3.12.2020 .
wtd_nts_property = 'P1653'  # .............................................................. 3.12.2020 .
# ==================================================================================================


class Wikidata(BotSite):
    def __init__(self):
        super(Wikidata, self).__init__(site=pywikibot.Site('wikidata', 'wikidata', user=_botconf['wikidata-user']))
        self.processed_item_id = None

    class CoordinateQueries:
        def __init__(self, simc, terc='', nts=''):
            self.simc = simc
            self.terc, self.nts = terc, nts
            self.sparql_pat = \
                f"""
                SELECT ?coord ?item ?itemLabel 
                WHERE
                {"{"}
                  ?item wdt:%(prop)s '%(terid)s'.
                  OPTIONAL {"{"}?item wdt:{coord_property} ?coord{"}"}.
                  SERVICE wikibase:label {"{"} bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". {"}"}
                {"}"}
                """

        @typecheck
        def construct(self, subsystem: str):
            propname = 'wdt_' + subsystem.lower() + '_property'
            ensure(propname in globals(), f'{subsystem} is not a valid TERYT subsystem')
            prop = eval(propname)
            ensure(prop, f'cannot construct a query: {subsystem} ID has not been provided')
            terid = getattr(self, subsystem.lower())
            return self.sparql_pat % dict(prop=prop, terid=terid)

    @typecheck
    def query(self, query, maximum: int = 1, index: str = None):
        result = tuple(pagegenerators.WikidataSPARQLPageGenerator(query, site=self.site))
        ensure(len(result) <= maximum, f'got {len(result)} results whilst maximum was set to {maximum}')
        return result[index] if isinstance(index, int) else result

    @typecheck
    def _get_item_id(self, *, simc: str, terc: str = '', nts: str = ''):
        cqueries = self.CoordinateQueries(simc=simc, terc=terc, nts=nts)
        results = {}
        for subsystem in teryt.subsystems:
            if eval(subsystem):
                results |= {subsystem: self.query(query=cqueries.construct(subsystem=subsystem))}
        for subresults in results.values():
            if subresults:
                ensure(len(subresults) == 1, f'Wikidata: {len(subresults)} results')
                self.processed_item_id = subresults[0]
                return self.processed_item_id

        raise ValueError(
            f'Wikidata ItemPage not found: '
            f'{representation("WikidataQuery-%r" % self.processed_page, simc=simc, terc=terc, nts=nts)}'
        )

    @typecheck
    def _get_item_source(self, item: pywikibot.ItemPage):
        try:
            return item.get()
        except pywikibot.exceptions.MaxlagTimeoutError:
            self._get_item_source(item=item)

    @typecheck
    def _get_item_coords(self, item: pywikibot.ItemPage):
        source = self._get_item_source(item)
        labels = tuple(dict(source['labels']).values())
        pagename = self.processed_page.title(with_ns=False, with_section=False, without_brackets=True)
        ensure(any([pagename in label for label in labels]), f'found item {item} has different name (label)')
        if coord_property not in item.claims:
            return {}
        coords = item.claims[coord_property][0].getTarget()
        return {'lat': coords.lat, 'lon': coords.lon, 'wikidata': self.processed_item_id}

    @processes_page
    def coords(self, _pagename, *, simc: str, terc: str = '', nts: str = ''):
        return self._get_item_coords(self._get_item_id(simc=simc, terc=terc, nts=nts))


class Wiki(BotSite):
    def __init__(self):
        super(Wiki, self).__init__(site=pywikibot.Site('pl', 'nonsensopedia', user=_botconf['user']))
        self.wikidata = Wikidata()
        self.ppterinfo = {}
        self.terdiv_cats = {
            'Kategoria:Województwo ': 'voivodship', 'Kategoria:Powiat ': 'powiat', 'Kategoria:Gmina ': 'gmina'
        }
        self.wrapper_cats = ('Kategoria:Powiaty w', 'Kategoria:Gminy w', 'Kategoria:Województwa w')
        self.trace = []
        self.doubling = []

    @typecheck
    def awaiting_articles(self, _category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        return tuple(pywikibot.Category(source=self.site, title=_category).articles())

    @typecheck
    @processes_page
    def terinfo(self, _pagename: str):
        def lookup(master: str) -> "dict":
            self.trace.append(master)
            if master not in self.doubling:
                subcategories = \
                    [subcat.title() for subcat in _wpage(master).categories() if 'hidden' not in subcat.categoryinfo]
                find(subcategories=subcategories, master=master)
            return self.ppterinfo

        def find(master: str, subcategories: list):
            if master in self.trace and all([wrapping_cat not in master for wrapping_cat in self.wrapper_cats]):
                self.doubling.append(master)
            [pull(sub) if label(sub) else lookup(sub) for sub in subcategories]

        def pull(sub: str):
            self.ppterinfo[self.terdiv_cats[label(sub)]] = sub.split(label(sub))[1]

        def label(sub: str):
            return next(iter([catpref for catpref in self.terdiv_cats if catpref in sub]), False)

        def fillempty(data: dict):
            simc = teryt.Simc()
            hierarchy = tuple(simc.loctype_nim.keys())
            for loctype in hierarchy:
                origin = simc.search(**data, loctype=loctype)
                if origin.parsed:
                    origin.transfer('nts') if origin.transfer('terc').parsed else do_nothing()
                    return origin
            raise BotError('Item not found in TERYT register')

        self.ppterinfo['name'] = self.processed_page.title(with_section=False, underscore=False, without_brackets=True)
        return fillempty(lookup(self.processed_page.title()))

