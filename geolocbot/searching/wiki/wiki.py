# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.tools import *
from geolocbot.libs import *
from geolocbot.loaders import *

# forgive me this
untitled_page = '<brak tytułu>'


def sets_category(meth: typing.Callable):
    def catsetter(cls, catname, *args, **kwargs):
        cls.page = pywikibot.Category(cls.site, catname)
        return meth(cls, catname, *args, **kwargs)
    return catsetter


def sets_page(meth: typing.Callable):
    def pagesetter(cls, pagename, *args, **kwargs):
        cls.page = pywikibot.Page(cls.site, pagename)
        return meth(cls, pagename, *args, **kwargs)
    return pagesetter


class GeoInfo:
    """ """


class Wiki:
    botconf = fetch_bot_config()

    def __init__(self):
        self.site = pywikibot.Site('pl', 'nonsensopedia', user=self.botconf['user'])
        self.src = pywikibot.Site('wikidata', 'wikidata', user=self.botconf['wikidata-user'])
        self.page = pywikibot.Page(self.site, untitled_page)

    @no_type_collisions
    @sets_category
    def get_awaiting_pages(self, _category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        return

    @no_type_collisions
    @sets_page
    def get_regional_info(self, _pagename: str):
        if not self.page.exists():
            return {}


wiki = Wiki()


def category(title=''): return pywikibot.Category(wiki.site, untitled_page if not title else title)
def page(title=''): return pywikibot.Page(wiki.site, untitled_page if not title else title)
