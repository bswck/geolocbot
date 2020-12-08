# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

# TODO: Error handling.


# import argparse
from geolocbot import *
from geolocbot.utils import getpagebyname, typecheck


class Geolocbot(wiki.WikiWrapper):
    def __init__(self, fallback=None, template_name='lokalizacja'):
        super().__init__()
        connecting.login()
        self._fallback = fallback or self.fallback
        self.nil = self.Nil()
        self.site = self.site
        self._template_name = template_name
        self._template_pat = \
            f'{"{{"}%(template_name)s|%(lat).6f, %(lon).6f|simc=%(simc)s|%(terc)swikidata=%(' \
            f'wikidata)s{"}}"}'
        self._postpone_pat = \
            f'* [[%(name)s|]] * {"{{/co|%(name)s|%(simc)s|%(terc)s|%(nts)s}}"} -- ~~~~~ | {"{{/p}}"}'
        self._data = {}
        self._comment_added = 'dodano lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_replaced = 'zastąpiono lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_postponed = 'usunięto lokalizację; zgłoszono stronę do przejrzenia'
        self._comment_postponed_report = 'zgłoszono stronę do przejrzenia'
        self._loc_pagename = ''

        self._template = ''
        self._locname = None
        self._lat = None
        self._lon = None
        self._wdtsource = None
        self._simc = None
        self._terc = None
        self._nts = None
        self._postpone = False

    class Nil:
        """ Marker for not found data. """
        def __repr__(self): return f'<not found>'
        def __bool__(self): return False

    @getpagebyname
    @typecheck
    def geolocate(self, _pagename: str):
        """
        Find the geolocation of Polish locality by its name identical with *_pagename*.

        Examples
        --------
        >>> g = Geolocbot()
        >>> g.geolocate('Pszczyna')
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
            simc, terc, nts = (transferred.get(sub.upper(), None) for sub in teryt.subsystems)
            ids = {'simc': simc.id, 'terc': getattr(terc, 'terid', ''), 'nts': getattr(nts, 'terid', '')}
            coords = self.base.geolocate(geoloc.name, nil=self.nil, **ids)
            result = {'name': pagename, 'coords': coords, **ids}
            output(pagename, '→', result)
            return result
        return geoloc  # <not found>

    @typecheck
    def geoloctemplate(self, lat: float, lon: float, simc: str, wikidata: str, terc: str = ''):
        terc = f'terc={terc}|' if terc else ''
        return self._template_pat % dict(
            template_name=self._template_name, lat=lat, lon=lon, simc=simc, terc=terc, wikidata=wikidata
        )

    def run_on_category(self, category='Kategoria:Strony z niewypełnionym szablonem lokalizacji'):
        articles = tuple(libs.pywikibot.Category(source=self.site, title=category).articles())
        for page in articles:
            self.run_on_page(page.title())

    @getpagebyname
    def proceed(self, _pagename):
        locpage = self.inst_page(self._loc_pagename)
        locpage_text = locpage.text
        prev_template = self.group_template(self._loc_pagename, 'lokalizacja')
        fmt = {'name': self._locname, 'lat': self._lat, 'lon': self._lon}
        if self._postpone:
            self.postpone()
            locpage.text = locpage_text.replace(f'\n{prev_template}', '')
            return locpage.save(self._comment_postponed)
        elif prev_template:
            locpage.text = locpage_text.replace(prev_template, self._template)
            return locpage.save(self._comment_replaced % fmt)
        locpage.text = self.insert(self._loc_pagename, text=self._template)
        return locpage.save(self._comment_added % fmt)

    @typecheck
    def run_on_page(self, pagename: str):
        self._data = self.geolocate(pagename)
        self._loc_pagename = pagename
        self._simc = self._data['simc']
        self._terc = self._data['terc']
        self._nts = self._data['nts']
        self._locname = self._data['name']
        coords = self._data['coords']
        if isinstance(coords, self.Nil):
            self._postpone = True
            return self.proceed(pagename)
        self._postpone = False
        self._lat = coords['lat']
        self._lon = coords['lon']
        self._wdtsource = coords['source'].title()
        self._template = self.geoloctemplate(
            lat=self._lat, lon=self._lon,
            simc=self._simc, wikidata=self._wdtsource,
            terc=self._terc
        )
        return self.proceed(pagename)

    def run(self, procedure): pass

    def fallback(self, page):
        pass

    def postpone(self, pagename='User:Stim/geolocbot/przejrzeć'):
        page = self.inst_page(pagename)
        fmt = {'name': self.processed_page.title(), 'simc': self._simc, 'terc': self._terc or '/',
               'nts': self._nts or '/'}
        page.text = self.insert(pagename, text=self._postpone_pat % fmt, prefixes=('\n *',))
        page.save(self._comment_postponed_report)
