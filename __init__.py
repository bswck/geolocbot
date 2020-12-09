# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

from geolocbot import *
from geolocbot.utils import getpagebyname, typecheck

args = prepare.argparser().parse_args()


class Geolocbot(wiki.WikiWrapper):
    def __init__(
            self,
            fallback=None,
            login=True,
            log=True,
            template_name='lokalizacja',
            quiet=False,
            errpage='User:Stim/geolocbot/błędy',
            postponepage='User:Stim/geolocbot/przejrzeć',
            sleepless=False
    ):
        super().__init__()
        if login:
            connecting.login()
        if quiet:
            utils.quiet = True
        if not log:
            utils.log = False
        self.args = None

        self.errpage = errpage
        self.postponepage = postponepage
        self.sleepless = sleepless
        self._fallback = fallback or self.fallback
        self.nil = self.Nil()
        self.site = self.site
        self._template_name = template_name
        self._template_pat = \
            f'{"{{"}%(template_name)s|%(lat).6f, %(lon).6f|simc=%(simc)s|%(terc)swikidata=%(' \
            f'wikidata)s{"}}"}'
        self._postpone_pat = f'* {"{{/co|%(name)s|%(simc)s|%(terc)s|%(nts)s|%(date)s|}}"}'
        self._error_pat = '\n%(name)s\n----\n<pre>\n%(traceback)s\n</pre>\n%(date)s\n'
        self._data = {}
        self._comment_added = 'dodano lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_replaced = 'zastąpiono lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_postponed = 'usunięto lokalizację; zgłoszono stronę do przejrzenia'
        self._comment_postponed_report = 'zgłoszono stronę do przejrzenia'
        self._comment_error_report = 'zgłoszono błąd'
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
    def template(self, lat: float, lon: float, simc: str, wikidata: str, terc: str = ''):
        terc = f'terc={terc}|' if terc else ''
        return self._template_pat % dict(
            template_name=self._template_name, lat=lat, lon=lon, simc=simc, terc=terc, wikidata=wikidata
        )

    def run_on_category(self, category):
        cat_prefixes = ['kategoria:', 'category:']
        if not any([category.lower().startswith(pref) for pref in cat_prefixes]):
            category = cat_prefixes[0].capitalize() + category
        if not self.sleepless:
            output(f"Haps! [[{category}]]")
        articles = tuple(libs.pywikibot.Category(source=self.site, title=category).articles())
        for page in articles:
            self.run_on_page(page.title())

    @getpagebyname
    def proceed(self, _pagename):
        locpage = self.instantiate_page(self._loc_pagename)
        locpage_text = locpage.text
        breakline = '\n'
        prev_template: str = self.search_for_template(self._loc_pagename, 'lokalizacja')
        fmt = {'name': self._locname, 'lat': self._lat, 'lon': self._lon}
        if self._postpone:
            self.postpone()
            output(f'Odkładam [[{self._loc_pagename}]] na później, zgłoszone gdzie trzeba.')
            locpage.text = locpage_text.replace(f'{prev_template}', '')
            return locpage.save(self._comment_postponed, quiet=True)
        elif prev_template:
            output(f'Riplejs, {self._template!r} do [[{self._loc_pagename}]] zamiast '
                   f'{prev_template.removesuffix(breakline).removesuffix(" ")!r}')
            locpage.text = locpage_text.replace(prev_template, self._template + '\n')
            return locpage.save(self._comment_replaced % fmt, quiet=True)
        locpage.text = self.insert(self._loc_pagename, text=self._template)
        output(f'Cyk, {self._template!r} do [[{self._loc_pagename}]]')
        return locpage.save(self._comment_added % fmt, quiet=True)

    @typecheck
    def run_on_page(self, pagename: str):
        self.instantiate_page(pagename)  # checkpoint
        output(f'Mlem: [[{pagename}]]')
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
        self._template = self.template(
            lat=self._lat, lon=self._lon,
            simc=self._simc, wikidata=self._wdtsource,
            terc=self._terc
        )
        return self.proceed(pagename)

    def run(self, arguments):
        try:
            output('Geolocbot v2.0™ by Błagamdziałaj®')
            awaiting_category = 'Kategoria:Strony z niewypełnionym szablonem lokalizacji'
            if arguments.page:
                return self.run_on_page(arguments.page)
            category = arguments.cat or awaiting_category
            if self.sleepless:
                while True:
                    self.run_on_category(category=category)
                    libs.time.sleep(30)
            return self.run_on_category(category=category)
        except SystemExit as sysexit:
            raise SystemExit from sysexit
        except utils.any_exception as exception:
            import traceback
            output(f'{utils.tc.red}ERROR{utils.tc.r}: {exception}')
            traceback = traceback.format_exc()
            self.fallback(traceback=traceback)

    def fallback(self, traceback):
        pagename = self.errpage
        page = self.instantiate_page(pagename)
        fmt = {'name': self._loc_pagename or '(Nie podczas przetwarzania miejscowości)', 'traceback': traceback,
               'date': self.date_time()}
        page.text = self.insert(pagename, text=self._error_pat % fmt, prefixes=('\n',))
        page.save(self._comment_error_report, quiet=True)

    def postpone(self):
        pagename = self.postponepage
        page = self.instantiate_page(pagename)
        fmt = {'name': self.processed_page.title(), 'simc': self._simc, 'terc': self._terc or '/',
               'nts': self._nts or '/', 'date': self.date_time()}
        page.text = self.insert(pagename, text=self._postpone_pat % fmt, prefixes=('\n *',))
        page.save(self._comment_postponed_report, quiet=True)


if __name__ == '__main__':
    if not args.debug:
        bot = Geolocbot(
            login=not args.no_wiki_login,
            quiet=args.shut_up,
            log=not args.dont_log,
            errpage=args.errpage,
            postponepage=args.postponepage,
            sleepless=args.sleepless
        )
        bot.run(arguments=args)
