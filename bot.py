""" The bot. """

# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license
import os

import pywikibot
from pywikibot import config

from geolocbot import wiki, connecting, prepare, utils, teryt
from geolocbot.utils import output


class Bot(wiki.WikiWrapper):
    """ Geolocbot. """
    def __init__(
            self,
            fallback=None,
            login=True,
            log=True,
            template_name='stopka',
            quiet=False,
            deferpage='User:Stim/geolocbot/przejrzeć',
    ):
        """ Initialize the bot. """
        super().__init__()
        if login:
            connecting.login()
        if quiet:
            utils.quiet = True
        if not log:
            utils.log = False
        self.args = None

        self.deferpage = deferpage
        self._fallback = fallback or self.fallback
        self._fallback_frame = None
        self.nil = self.Nil()
        self.site = self.site
        self._template_name = template_name
        self._template_pat = \
            f'{"{{"}%(template_name)s|lokalizacja=%(lat).6f, %(lon).6f|simc=%(simc)s|%(terc)swikidata=%(' \
            f'wikidata)s{"}}"}'
        self._defer_pat = f'* {"{{/co|%(name)s|%(simc)s|%(terc)s|%(nts)s|%(date)s|}}"}'
        self._error_pat = '\n%(name)s\n%(frame)s\n\n~~~~~~~~~~~~\n%(traceback)s\n~~~~~~~~~~~~\n%(date)s\n'
        self._data = {}
        self._comment_added = 'dodano lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_replaced = 'zastąpiono lokalizację (%(name)s: %(lat).4f, %(lon).4f)'
        self._comment_deferred = 'usunięto lokalizację; zgłoszono stronę do przejrzenia'
        self._comment_deferred_report = 'zgłoszono stronę do przejrzenia'
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
        self._defer = False

    class Nil:
        """ Marker for not found data. """
        def __repr__(self): return '<not found>'
        def __getitem__(self, item): return self
        def __bool__(self): return False

    @utils.getpagebyname
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
        self._loc_pagename = pagename
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

    def template(self, lat: float, lon: float, simc: str, wikidata: str, terc: str = ''):
        """
        Construct geolocation template.
        See:
            (pl) https://nonsa.pl/wiki/Szablon:Lokalizacja

        Parameters
        ----------
        lat : float
            Latitude.
        lon : float
            Longitude.
        simc: str
            SIMC identificator.
        wikidata
            Wikidata ItemPage title, e.g. 'Q270'.
        terc: str
            TERC identificator.

        Returns
        -------

        """
        terc = f'terc={terc}|' if terc else ''
        return self._template_pat % dict(
            template_name=self._template_name, lat=lat, lon=lon, simc=simc, terc=terc, wikidata=wikidata
        )

    def run_on_category(self, cat):
        """
        Run the bot on a given category.

        Parameters
        ----------
        cat : str
            Name of the category.
        """
        cat_prefixes = ['kategoria:', 'category:']
        if not any([cat.lower().startswith(pref) for pref in cat_prefixes]):
            cat = cat_prefixes[0].capitalize() + cat

        output(f"Haps! [[{cat}]]")
        articles = tuple(pywikibot.Category(source=self.site, title=cat).articles())
        for page in articles:
            self.run_on_page(page.title())

    @utils.getpagebyname
    def proceed(self, _pagename):
        """
        Adapt to certain factors; indicate further behavior of bot in context of a page.

        Parameters
        ----------
        _pagename: str
            Name of the page to be processed.
        """
        locpage = self.instantiate_page(self._loc_pagename)
        locpage_text = locpage.text
        prev_template: str = self.search_for_template(self._loc_pagename, 'lokalizacja')
        fmt = {'name': self._locname, 'lat': self._lat, 'lon': self._lon}
        if self._defer:
            self.defer()
            output(f'Odkładam [[{self._loc_pagename}]] na później, zgłoszone gdzie trzeba.')
            locpage.text = locpage_text.replace(f'{prev_template}', '')
            return locpage.save(self._comment_deferred, quiet=True)
        elif prev_template:
            output(f'Riplejs, {self._template!r} do [[{self._loc_pagename}]] zamiast '
                   f'{prev_template!r}')
            locpage.text = locpage_text.replace(prev_template, self._template + '\n')
            return locpage.save(self._comment_replaced % fmt, quiet=True)
        locpage.text = self.insert(self._loc_pagename, text=self._template)
        output(f'Cyk, {self._template!r} do [[{self._loc_pagename}]]')
        return locpage.save(self._comment_added % fmt, quiet=True)

    def run_on_page(self, pagename: str):
        """
        Run the bot on a given page.

        Parameters
        ----------
        pagename : str
            Name of the page.
        """
        self.instantiate_page(pagename)  # checkpoint
        output(f'Mlem: [[{pagename}]]')
        self._data = self.geolocate(pagename)
        if isinstance(self._data, self.Nil):
            self._simc = None
            self._terc = None
            self._nts = None
            self._locname = None
            self._defer = True
            return self.proceed(pagename)
        self._simc = self._data['simc']
        self._terc = self._data['terc']
        self._nts = self._data['nts']
        self._locname = self._data['name']
        coords = self._data['coords']
        if isinstance(coords, self.Nil):
            self._defer = True
            return self.proceed(pagename)
        self._defer = False
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
        """
        Run Geolocbot.

        Parameters
        ----------
        arguments : Namespace
            Arguments.
        """
        try:
            output('Geolocbot v2.0™ by Błagamdziałaj®')
            default_cat = 'Kategoria:Strony z niewypełnionym szablonem lokalizacji'
            if arguments.page:
                return self.run_on_page(arguments.page)
            cat = arguments.cat or default_cat
            return self.run_on_category(cat=cat)
        except SystemExit as sysexit:
            raise SystemExit from sysexit
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except BaseException as exception:
            import traceback
            output(f'ERROR: {exception}')
            traceback = traceback.format_exc()
            self.fallback(traceback=traceback)
        finally:
            self.defer()

    def fallback(self, traceback):
        """ Report an error on a specified page. """
        fmt = {'name': self._loc_pagename or '(Nie podczas przetwarzania miejscowości)', 'traceback': traceback,
               'frame': self._fallback_frame or '(reprezentacja obiektu podsystemu niedostępna)',
               'date': self.date_time()}
        output(self._error_pat % fmt, file='stderr')

    def defer(self):
        """ Defer supplying geolocation template to a page, reporting the deferment on a specified page. """
        pagename = self.deferpage
        page = self.instantiate_page(pagename)
        fmt = {'name': self._loc_pagename, 'simc': self._simc or '/', 'terc': self._terc or '/',
               'nts': self._nts or '/', 'date': self.date_time()}
        if f'{self._loc_pagename}' not in page.text:
            page.text = self.insert(pagename, text=self._defer_pat % fmt, prefixes=('\n *',))
            page.save(self._comment_deferred_report, quiet=True)


if __name__ == '__main__':
    args = prepare.argparser().parse_args()
    config.password_file = os.environ.get(
        'GEOLOCBOT_PASSWORD_FILE',
        os.path.join(os.path.dirname(__file__), 'user-password.py')
    )
    if not args.debug:
        bot = Bot(
            login=not args.no_wiki_login,
            quiet=args.shut_up,
            log=not args.dont_log,
            deferpage=args.deferpage,
        )
        bot.run(arguments=args)
