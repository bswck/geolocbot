# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.tools import *
from geolocbot.exceptions import *
from geolocbot.libs import *
from geolocbot.loaders import *
import geolocbot.searching.teryt as teryt


__all__ = ('wiki',)

_botconf = fetch_bot_config()


class BotSite:
    def __init__(self, site: pywikibot.Site):
        self.site = site
        self.processed_page = pywikibot.Page(self.site, 'Main Page')  # default


def _wpage(title):
    return pywikibot.Page(source=wiki.site, title=title)


def _processes_page(callable_: typing.Callable):
    def wrapper(class_, pagename: str, *arguments_, **keyword_arguments):
        class_.processed_page, arguments = pywikibot.Page(class_.site, pagename), (class_, pagename, *arguments_)
        return callable_(*arguments, **keyword_arguments)

    return wrapper


coord_property = 'P625'
# To do in Wikidata: replace NTS IDs from 2005 confused with TERC IDs (which is called "TERYT" municipality code)
# with proper, up to date TERC IDs.
#
# See: https://www.wikidata.org/wiki/Property:P1653
# ==================================================================================================
simc_property = 'P4046'  # ............................................................. 3.12.2020 .
terc_property = 'P1653'  # ............................................................. 3.12.2020 .
nts_property = 'P1653'  # .............................................................. 3.12.2020 .
# ==================================================================================================


class Wikidata(BotSite):
    def __init__(self):
        super(Wikidata, self).__init__(site=pywikibot.Site('wikidata', 'wikidata', user=_botconf['wikidata-user']))
        self.processed_item_id = None

    class CoordinateQueries:
        def __init__(self, simc, terc='', nts=''):
            self.simc = simc
            self.terc, self.nts = terc, nts
            self.simc_property = simc_property
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
            propname = subsystem.lower() + '_property'
            ensure(propname in globals(), f'{subsystem} is not a valid TERYT subsystem')
            prop = eval(propname)
            ensure(prop, f'cannot construct a query: {subsystem} ID has not been provided')
            terid = getattr(self, subsystem.lower())
            return self.sparql_pat % dict(prop=prop, terid=terid)

    @typecheck
    def query(self, query, maximum: int = 1, index: str = None):
        result = tuple(pywikibot.pagegenerators.WikidataSPARQLPageGenerator(query, site=self.site))
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

        raise ValueError(f'Wikidata ItemPage not found (simc={simc!r}, terc={terc!r}, nts={nts!r})')

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
        pagename = self.processed_page.title(with_ns=False, without_brackets=True)
        ensure(any([pagename in label for label in labels]), 'item has different name (label)')
        if coord_property not in item.claims:
            return {}
        coordinate_obj = item.claims[coord_property][0].getTarget()
        return {'lat': coordinate_obj.lat, 'lon': coordinate_obj.lon, 'wikidata': self.processed_item_id}

    @_processes_page
    def coords(self, _pagename, *, simc: str, terc: str = '', nts: str = ''):
        return self._get_item_coords(self._get_item_id(simc=simc, terc=terc, nts=nts))


class Wiki(BotSite):
    def __init__(self):
        super(Wiki, self).__init__(site=pywikibot.Site('pl', 'nonsensopedia', user=_botconf['user']))
        self.data_repo = Wikidata()
        self._ppterinf = {}
        self.rcps = {'Kategoria:Województwo ': 'voivodship', 'Kategoria:Powiat ': 'powiat', 'Kategoria:Gmina ': 'gmina'}
        self.wrapper_cats = ('Kategoria:Powiaty w', 'Kategoria:Gminy w', 'Kategoria:Województwa w')
        self.trace = []
        self.doubling = []

    @typecheck
    def awaiting_articles(self, _category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        return tuple(pywikibot.Category(source=self.site, title=_category).articles())

    @typecheck
    @_processes_page
    def terinfo(self, _pagename: str):
        def lookup(master: str) -> "dict":
            self.trace.append(master)
            if master not in self.doubling:
                subcategories = \
                    [subcat.title() for subcat in _wpage(master).categories() if 'hidden' not in subcat.categoryinfo]
                find(subcategories=subcategories, master=master)
            return self._ppterinf

        def find(master: str, subcategories: list):
            if master in self.trace and all([wrapping_cat not in master for wrapping_cat in self.wrapper_cats]):
                self.doubling.append(master)
            [pull(sub) if label(sub) else lookup(sub) for sub in subcategories]

        def pull(sub: str):
            self._ppterinf[self.rcps[label(sub)]] = sub.split(label(sub))[1]

        def label(sub: str):
            return next(iter([catpref for catpref in self.rcps if catpref in sub]), False)

        def fillempty(data: dict):
            simc = teryt.Simc()
            hierarchy = tuple(simc.loctype_nim.keys())
            for loctype in hierarchy:
                origin = simc.search(**data, loctype=loctype)
                if origin.parsed:
                    origin.transfer('nts') if origin.transfer('terc').parsed else do_nothing()
                    return origin
            raise BotError('Item not found in TERYT register')

        self._ppterinf['name'] = self.processed_page.title(with_section=False, underscore=False, without_brackets=True)
        return fillempty(lookup(self.processed_page.title()))


wiki = Wiki()
