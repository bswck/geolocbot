# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.tools import *
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


def _process_page(callable_: typing.Callable):
    def wrapper(class_, pagename, *arguments_, **keyword_arguments):
        class_.processed_page, arguments = pywikibot.Page(class_.site, pagename), (class_, pagename, *arguments_)
        return callable_(*arguments, **keyword_arguments)

    return wrapper


class Wikidata(BotSite):
    coord_property = 'P625'
    # To do in Wikidata: replace NTS IDs from 2005 confused with TERC IDs (which is called "TERYT" municipality code)
    # with proper, up to date TERC IDs.
    #
    # See: https://www.wikidata.org/wiki/Property:P1653
    # ==================================================================================================
    simc_property = 'P1653'  # ............................................................. 3.12.2020 .
    terc_property = 'P4046'  # ............................................................. 3.12.2020 .
    nts_property = 'P4046'  # .............................................................. 3.12.2020 .
    # ==================================================================================================

    def __init__(self):
        super(Wikidata, self).__init__(site=pywikibot.Site('wikidata', 'wikidata', user=_botconf['wikidata-user']))

    class CoordinateQueries:
        def __init__(self, simc, terc='', nts=''):
            self.simc = simc
            self.terc, self.nts = terc, nts
            self.simc_property = 'P1653'
            self.sparql_pat = \
                """
                SELECT ?coord ?item ?itemLabel 
                WHERE
                {
                  ?item wdt:{prop} '{terid}'.
                  OPTIONAL {?item wdt:%(coord_property)s ?coord}.
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],pl". }
                }
                """ % dict(coord_property=Wikidata.coord_property)

        @typecheck
        def get(self, subsystem: str):
            propname = subsystem.lower() + '_property'
            ensure(hasattr(self, propname), f'{subsystem} is not a valid TERYT subsystem')
            prop = getattr(self, propname)
            ensure(prop, f'cannot construct a query: {subsystem} ID has not been provided')
            terid = getattr(self, subsystem.lower())
            return self.sparql_pat.format(prop=prop, terid=terid)

    @typecheck
    def query(self, query, maximum: int = 1, index: str = None):
        result = tuple(pywikibot.pagegenerators.WikidataSPARQLPageGenerator(query, site=self.site))
        ensure(len(result) <= maximum, f'got {len(result)} results whilst maximum was set to {maximum}')
        return result[index] if isinstance(index, int) else result

    @typecheck
    def _get_item_id(self, *, simc: str, terc: str = '', nts: str = ''):
        query = self.CoordinateQueries(simc=simc, terc=terc, nts=nts)
        results = {}
        for subsystem in teryt.subsystems:
            if eval(subsystem):
                results |= {subsystem: self.query(query=query.get(subsystem=subsystem))}
        for result in results.values():
            if result:
                return result
        return None

    def _get_item_source(self, item: pywikibot.ItemPage):
        try:
            return item.get()
        except pywikibot.exceptions.MaxlagTimeoutError:
            self._get_item_source(item=item)

    def _get_item_coords(self, item_id):
        item = pywikibot.ItemPage(self.site, item_id)
        source = self._get_item_source(item)
        labels = source['labels']
        pagename = self.processed_page.title(with_ns=False, with_brackets=False)
        ensure(any([label.startswith(pagename) for label in labels]), 'item has different name (label)')
        if self.coord_property not in item.claims:
            return {}
        coordinate_obj = item.claims[self.coord_property][0].getTarget()
        return {'lat': coordinate_obj.lat, 'lon': coordinate_obj.lon}

    def coords(self, *, _pagename, simc: str, terc: str = '', nts: str = ''):
        return self._get_item_coords(self._get_item_id(simc=simc, terc=terc, nts=nts).title())


class Wiki(BotSite):
    def __init__(self):
        super(Wiki, self).__init__(site=pywikibot.Site('pl', 'nonsensopedia', user=_botconf['user']))
        self.data_repo = Wikidata()
        self._ppterinf = {}
        self.rcps = {'Kategoria:Województwo ': 'voivodship', 'Kategoria:Powiat ': 'powiat', 'Kategoria:Gmina ': 'gmina'}
        self.wrappers = ('Kategoria:Powiaty w', 'Kategoria:Gminy w', 'Kategoria:Województwa w')
        self.trace = []

    @typecheck
    def awaiting_articles(self, _category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        return tuple(pywikibot.Category(source=self.site, title=_category).articles())

    @typecheck
    @_process_page
    def terinfo(self, _pagename: str):
        def lookup(master: str) -> "dict":
            if master not in self.trace:
                subcategories = \
                    [subcat.title() for subcat in _wpage(master).categories() if 'hidden' not in subcat.categoryinfo]
                find(subcategories=subcategories, master=master)
            return self._ppterinf

        def find(master: str, subcategories: list):
            self.trace += master if master not in self.wrappers else []
            [pull(sub) if label(sub) else lookup(sub) for sub in subcategories]

        def pull(sub: str):
            self._ppterinf[self.rcps[label(sub)]] = sub.split(label(sub))[1]

        def label(sub: str):
            return next(iter([catpref for catpref in self.rcps if catpref in sub]), False)

        def fillempty(data: dict) -> "dict":
            hierarchy = tuple(teryt.simc.locality_type_compt.keys())
            for loctype in hierarchy:
                origin = teryt.simc.search(**data, locality_type=loctype)
                if origin.parsed:
                    origin.transfer('nts') if origin.transfer('terc').parsed else do_nothing()
                    return origin.to_dict()
            return data

        self._ppterinf['name'] = self.processed_page.title(with_section=False, underscore=False, without_brackets=True)
        return fillempty(lookup(self.processed_page.title()))


wiki = Wiki()
