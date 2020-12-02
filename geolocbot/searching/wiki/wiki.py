# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.tools import *
from geolocbot.libs import *
from geolocbot.loaders import *
import geolocbot.searching.teryt as teryt

empty_title_mark = 'HTTP 404'


def pagesetter(callable_: typing.Callable):
    def wrap(class_, pagename, *arguments_, **keyword_arguments):
        class_.processed_page, arguments = pywikibot.Page(class_.site, pagename), (class_, pagename, *arguments_)
        return callable_(*arguments, **keyword_arguments)
    return wrap


class Wiki:
    def __init__(self):
        self.botconf = fetch_bot_config()
        self.site = pywikibot.Site('pl', 'nonsensopedia', user=self.botconf['user'])
        self.src = pywikibot.Site('wikidata', 'wikidata', user=self.botconf['wikidata-user'])
        self.processed_page = pywikibot.Page(self.site, empty_title_mark)
        self._ppreginf = {}
        self.rcps = {'Kategoria:Województwo ': 'voivodship', 'Kategoria:Powiat ': 'powiat', 'Kategoria:Gmina ': 'gmina'}
        self.trace = []

    @no_type_collisions
    def awaiting_pages(self, _category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        return tuple(pywikibot.Category(source=self.site, title=_category).articles())

    @no_type_collisions
    @pagesetter
    def regional_info(self, _pagename: str):
        def lookup(master: str) -> "dict":
            if master not in self.trace:
                subcategories = \
                    [subcat.title() for subcat in page(master).categories() if 'hidden' not in subcat.categoryinfo]
                find(subcategories=subcategories, master=master)
            return self._ppreginf

        def find(master: str, subcategories: list):
            self.trace.append(master)
            [pull(sub) if label(sub) else lookup(sub) for sub in subcategories]

        def pull(sub: str): self._ppreginf[self.rcps[label(sub)]] = sub.split(label(sub))[1]
        def label(sub: str): return next(iter([catpref for catpref in self.rcps if catpref in sub]), False)

        def fillempty(data: dict) -> "dict":
            new = teryt.terc.search(**data, function='powiat')  # hierarchized
            return new.to_dict() if new.parsed else data

        self._ppreginf['name'] = self.processed_page.title(with_section=False, underscore=False, without_brackets=True)
        return fillempty(lookup(self.processed_page.title()))


wiki = Wiki()


def page(title=''):
    return pywikibot.Page(source=wiki.site, title=title)
