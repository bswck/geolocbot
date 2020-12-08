# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

# import argparse
from geolocbot import *
from geolocbot.utils import getpagebyname, typecheck


class Geolocbot(wiki.WikiWrapper):
    def __init__(self, fallback=None, geoloctemplate_name='lokalizacja'):
        super().__init__()
        self._fallback = fallback or self.fallback
        self.nil = self.Nil()
        self.site = self.site
        self.processed_page = self.processed_page
        self.geoloctemplate_name = geoloctemplate_name
        self.geoloctemplate_pat = \
            f'{"{{"}%(template_name)s|%(lat).10f, %(lon).10f|simc=%(simc)s|%(terc)swikidata=%(' \
            f'wikidata)s{"}}"}'

    class Nil:
        """ Marker for not found data. """
        def __repr__(self): return f'{utils.tc.grey}<{utils.tc.red}not found{utils.tc.grey}>{utils.tc.r}'
        def __bool__(self): return False

    @getpagebyname
    @typecheck
    def geolocate(self, _pagename: str):
        """
        Find the geolocation of Polish locality by its name identical with *_pagename*.

        Examples
        --------
        >>> Geolocbot.geolocate('Pszczyna')
        TODO

        Returns
        -------
        dict
            Pagename, coordinates (latitude, longitude, source Wikidata ItemPage),
            IDs in TERYT subsystems (SIMC ID – obligatory, TERC ID – if possible, NTS (2005) ID – if possible).
        """
        pagename = self.processed_page.title()
        geoloc = self.loc_terinfo(pagename, nil=self.nil)
        if geoloc:
            transferred = dict(teryt.transferred_searches(geoloc.name))
            simc, terc, nts = (transferred[sub.upper()] for sub in teryt.subsystems)
            ids = {'simc': simc.id, 'terc': getattr(terc, 'terid', ''), 'nts': getattr(nts, 'terid', '')}
            coords = self.base.geolocate(geoloc.name, nil=self.nil, **ids)
            result = {'name': pagename, 'coords': coords, **ids}
            output(pagename, '→', result)
            return result
        return geoloc  # <not found>

    @typecheck
    def geoloctemplate(self, lat: float, lon: float, simc: str, wikidata: str, terc: str = ''):
        terc = f'terc={terc}|' if terc else ''
        return self.geoloctemplate_pat % dict(
            template_name=self.geoloctemplate_name, lat=lat, lon=lon, simc=simc, terc=terc, wikidata=wikidata
        )

    def run_on_category(self, category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        articles = tuple(pywikibot.Category(source=self.site, title=category).articles())
        for page in articles:
            self.run_on_page(page)

    @typecheck
    def run_on_page(self, pagename: str):
        data = self.geolocate(pagename)
        if isinstance(data, self.Nil):
            return False
        coords = data['coords']
        name, lat, lon, simc, terc = data['name'], coords['lat'], coords['lon'], data['simc'], data['terc']
        wikidata = coords['source'].title()
        template = self.geoloctemplate(lat=lat, lon=lon, simc=simc, wikidata=wikidata, terc=terc)
        self.insert(pagename, template, f'dodano lokalizację ({name}: {lat:.4f}, {lon:.4f})')
        return True

    def run(self, procedure): pass

    def fallback(self, page):
        pass
