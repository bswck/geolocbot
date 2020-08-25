from glbconfig import config
from time import strftime
import csv
import pandas
import pywikibot
import sys
import traceback


class Geolocbot(object):
    """
    Base class binding all non-exception classes in the Geolocbot project.
    """
    Site = pywikibot.Site(config['wiki']['lang'], config['wiki']['family'])

    def do(self, q, **kw):
        if 'sep' not in kw:
            kw['sep'] = '|'
        if isinstance(q, str):
            if '(' in q and ')' in q:
                if q.count('(') == q.count(')'):
                    for _i in range(q.count('(')):
                        _qt = q[q.index('(') + 1:q.index(')')]
                        if sep in _qt:
                            args = _qt.split(sep)
                            aux = q[:q.index('(') - 1]
                            if sep in aux:
                                cmd = aux[aux.rindex(sep):]
                            else:
                                cmd = aux
                            if cmd[0] == config['interface']['command-prefix']:
                                expression = '%s (%s)' % (cmd, sep.join(args))
                                generator = sep.join(['%s %s' % (cmd, arg) for arg in args])
                                q = q.replace(expression, generator, 1)
            if sep in q:
                q = q.split(sep)
        for task in q:
            if len(task) >= 5:
                if task[0] == config['interface']['command-prefix']:
                    try:
                        command = task[1:].split()
                        arg = ''
                        if len(command) == 2:
                            arg = command[1]
                        elif len(command) > 2:
                            arg = " ".join(command[1:])
                        command = command[0]
                        if command == 'exit':
                            arg = {'msg': arg}
                        if isinstance(arg, dict):
                            return getattr(self.Commands, command)(**arg)
                        elif isinstance(arg, str):
                            return getattr(self.Commands, command)(arg)
                    except AttributeError as attributeerror:
                        raise AttributeError("no command named '%s' [AttributeError: %s]" % (command, attributeerror))
                elif not pywikibot.Page(Geolocbot.Site, task).exists:
                    raise PageDoesNotExist(task)
                else:
                    geo = WikiArticle(task).get(**kw)
                    if kw:
                        if 'quiet' in kw:
                            print(geo) if not kw['quiet'] else None
                    return geo

    class Commands(object):
        """
        Commands as class methods.
        """
        @staticmethod
        def exit(msg=''):
            exit(msg)

        @staticmethod
        def list():
            return PageContentReader.ReadAsList(config['wiki']['work-list']['src'])

        @staticmethod
        def overwrite(arg):
            return Geolocbot().do(arg, ignore_log=1)

        @staticmethod
        def changesettings():
            # TODO
            pass

        @staticmethod
        def savesettings():
            # TODO
            pass

        pass

    @staticmethod
    def run(*args, quiet=False):
        try:
            data = {}
            if not args:
                task = UserQuery.prompt()
                if isinstance(task, list):
                    args = task
                elif isinstance(task, str):
                    args = [task]
            data.update(Geolocbot().do(args, sep='|'))
            if not quiet:
                print(data)
            return data
        except:
            exc_info = {
                'name': sys.exc_info()[0].__name__,
                'msg': '',
                'tb': traceback.format_exc()
            }
            if str(sys.exc_info()[1]) != 'None':
                exc_info['msg'] = f'{sys.exc_info()[1]}\n'

            ExceptionSnitch(exc_info)

    pass


class Rectifier(Geolocbot):
    """
    Class formatting WikiArticle labels.
    """
    def FormatLabel(self, label: str):
        s = self.Site
        label = pywikibot.Page(s, label).title(with_ns=False)
        if pywikibot.Page(s, label).isRedirectPage():
            label = pywikibot.Page(s, label).getRedirectTarget().title(with_section=False)
        return label

    def FormatDbLabel(self, label: str):
        s = self.Site
        dblabel = pywikibot.Page(s, label).title(without_brackets=True)
        return dblabel

    pass


class WikiArticle(Geolocbot):
    """
    Object storing data about article in a working wiki.
    """
    def __init__(self, page_title: str):
        super().__init__()
        self._T = page_title
        self.GeoData = {}
        self.Categories = []
        self.quiet = False
        try:
            log = open(f"log-{strftime('%d-%m-%Y')}.txt", 'r')
            src = log.read()
            logged_data = "[%s:%s] {'%s': {" % \
                          (self.Site.family.name, self.Site.code, self._T)
            fam_info_len = len(f'[{self.Site.family.name}:{self.Site.code}] ')
            if logged_data in src:
                from_line = src[src.index(logged_data) + fam_info_len:]
                categories = from_line[from_line.index('} ') + 2:]
                categories = categories[:categories.index('] ') + 1]
                self.Categories = eval(categories)
                geodata = from_line[:from_line.index('}} ') + 2]
                self.GeoData = eval(geodata)
                log.close()
        except FileNotFoundError:
            pass
        self._Label = ''
        self._DbLabel = ''
        if self._T:
            self.Page = pywikibot.Page(self.Site, self.Label)

    def get(self, **kw):
        if 'quiet' not in kw:
            kw['quiet'] = False
        if 'ignore_log' not in kw:
            kw['ignore_log'] = False
        PageContentReader.geodata = {}
        if kw['quiet']:
            self.quiet = True
        if kw['ignore_log']:
            self.Categories = []
            self.GeoData = {}
        if getattr(self, 'Categories') == []:
            self.Categories = self._Categories()
        if getattr(self, 'GeoData') == {}:
            self.GeoData = {self.OldTitle: PageContentReader.geodata}
        if not kw['quiet']:
            print('Uzyskano dane artykułu.')
        return self.GeoData

    @property
    def OldTitle(self):
        return self._T

    @property
    def Title(self):
        return self.Label

    @property
    def Label(self):
        if not self._Label:
            self._Label = Rectifier().FormatLabel(self._T)
        return self._Label

    @property
    def DbLabel(self):
        if not self._DbLabel:
            self._DbLabel = Rectifier().FormatDbLabel(self._T)
        return self._DbLabel

    def _Categories(self):
        return PageContentReader.CategoryGetter(self.Label)

    def __str__(self):
        return f"WikiArticle({self._T})"

    def __del__(self):
        attrs = ['Categories', 'GeoData']
        if all(all([hasattr(self, attr), getattr(self, 'GeoData')]) for attr in attrs):
            src = ''
            try:
                log = open(f"log-{strftime('%d-%m-%Y')}.txt", 'r+')
                src = log.read()
                log.close()
            except FileNotFoundError:
                pass
            log = open(f"log-{strftime('%d-%m-%Y')}.txt", 'w+')
            ln = f"[{self.Site.family.name}:{self.Site.code}] {self.GeoData} {self.Categories} {strftime('%H:%M:%S')}\n"
            log.write(ln + src)
            log.close()

    pass


class Search(Geolocbot):
    """
    TODO
    """
    # def __init__(self, wikiarticle=WikiArticle):
    #     if not isinstance(wikiarticle, WikiArticle):
    #         raise TypeError(f"Geolocbot Search expected WikiArticle type, got {type(wikiarticle).__name__} instead")
    #     self.query = wikiarticle
    pass


WikiArticle.Search = Search


class TERYT(Search):
    """
    Class working on TERYT localities register.
    """
    def __init__(self):
        self.dataframes = self.import_dataframes()

    @staticmethod
    def import_dataframes():
        basic_cols = ['WOJ', 'POW', 'GMI', 'NAZWA']
        terc_db = pandas.read_csv('TERC.csv', sep=';', usecols=[*basic_cols, 'RODZ', 'NAZWA_DOD']).fillna(0)
        simc_db = pandas.read_csv('SIMC.csv', sep=';', usecols=[*basic_cols, 'RODZ_GMI', 'NAZWA', 'SYM'])
        simc_db = simc_db.fillna(0)
        nts_db = pandas.read_csv("NTS.csv", sep=';').fillna(0)
        dataframes = [simc_db, terc_db, nts_db]

        for db in dataframes:
            int_float_col = db.select_dtypes(include=['int64', 'float64'])
            for col in int_float_col.columns.values:
                db[col] = db[col].astype(float).astype(int).astype(str)
                zfill2_cols = ['WOJ', 'POW', 'GMI']
                for _col in zfill2_cols:
                    db[_col] = db[_col].astype(str).str.zfill(2)

        simc_db['SYM'] = simc_db['SYM'].astype(str).str.zfill(7)
        dataframes = {'SIMC': simc_db,
                      'TERC': terc_db,
                      'NTS': nts_db}
        return dataframes

    def terc(self, **cdtmap):
        terc = self.dataframes['TERC']
        for _ in range(len(terc.keys())):
            _t = 0
            hierarchy = ['GMI', 'POW', 'WOJ']
            while _t != len(cdtmap):
                dest = terc.loc[(terc[list(cdtmap)] == pd.Series(cdtmap)).all(axis=1)]
                if dest.empty():
                    del cdtmap[hierarchy[_t]]
                _t += 1


class Wikidata(Search):
    pass


TERYT = TERYT()
Search.TERYT = TERYT
Wikidata = Wikidata()
Search.Wikidata = Wikidata


class UserQuery(Geolocbot):
    @staticmethod
    def prompt():
        q = ''
        while not q or q.isspace():
            q = input('>>>> ')
        return q


class PageContentReader(Geolocbot):
    def __init__(self):
        super().__init__()
        self.cats_to_ommit = []
        self.geodata = {}
        self.items_list_openning_tag = config['wiki']['work-list']['openning-tag']
        self.items_list_closing_tag = config['wiki']['work-list']['closing-tag']

    # TODO: this method doesn't have a propper structure and name
    @staticmethod
    def care_about_status(locality_name, status=None):
        terc_db = TERYT.dataframes['TERC']
        locality_name = Rectifier().FormatDbLabel(locality_name)
        if status is not None:
            df = terc_db.loc[(terc_db['NAZWA'] == locality_name) &
                             (terc_db['NAZWA_DOD'].str.contains(status))]
            if df.empty:
                return False
            else:
                df = df.reset_index()
                return df.at[0, 'NAZWA']
        else:
            target = PageContentReader.care_about_status(locality_name, status='powiat')
            if target is False:
                target = PageContentReader.care_about_status(locality_name.upper(), status='województwo')
                if not target.empty:
                    terc_id_shortened = target.at[0, 'WOJ']
                    return terc_id_shortened
                else:
                    return False

            else:
                target = target.reset_index()
                terc_id_shortened = f"{target.at[0, 'WOJ']}{target.at[0, 'POW']}"
                return terc_id_shortened

    def CategoryGetter(self, pg_title):
        article_categories = [
            cat.title() for cat in pywikibot.Page(self.Site, pg_title).categories()
            if 'hidden' not in cat.categoryinfo
        ]
        PageContentReader.GeoDataSelector(article_categories, pg_title)
        return article_categories

    def GeoDataSelector(self, article_categories: list, pg_title):
        cat_teritorial_parts = ['Kategoria:Gmina ', 'Kategoria:Powiat ', 'Kategoria:Województwo ']
        best_cats = ['Kategoria:Miasta w', 'Kategoria:Powiaty w', 'Kategoria:Gminy w',
                     f'Kategoria:{pg_title}']
        ac = article_categories.copy()
        for __c in article_categories.copy():
            for _c in best_cats + cat_teritorial_parts:
                if _c in __c:
                    article_categories.remove(__c)
                    ac = [__c] + article_categories
        article_categories = ac
        for i in range(len(article_categories)):
            if len(self.geodata.keys()) < 3:
                ca_cat = article_categories[i]
                page = pywikibot.Page(self.Site, pg_title)
                text = page.text
                district_signs = ['osiedl', 'dzielnic', 'częścią', 'część']
                teritorial_parts_an = ['GMI', 'POW', 'WOJ']

                if any(district_sign in text[:250] for district_sign in district_signs):
                    Locality.IsDistrict = True

                for _i in range(3):
                    if teritorial_parts_an[_i] not in self.geodata and cat_teritorial_parts[_i] in ca_cat:
                        value = Rectifier().FormatDbLabel(ca_cat.replace(cat_teritorial_parts[_i], ''))
                        info = {teritorial_parts_an[_i]: (value.lower()
                                                          if teritorial_parts_an[_i] == 'POW'
                                                          else value.title()
                                                          if teritorial_parts_an[_i] == 'GMI'
                                                          else value.upper())}
                        self.geodata.update(info)

                if 'Kategoria:Ujednoznacznienia' in ca_cat:
                    raise ValueError('Podana strona to ujednoznacznienie.')

                elif any(c in ca_cat for c in best_cats) and all(tp not in self.geodata for tp in teritorial_parts_an):
                    pow_stat = PageContentReader.care_about_status(pg_title, status='powiat')
                    gmi_stat = PageContentReader.care_about_status(pg_title, status='gmina')
                    if pow_stat is not False:
                        new_geodata = {'POW': f'{pow_stat}'}
                        self.geodata.update(new_geodata)
                    if gmi_stat is not False:
                        new_geodata = {'GMI': f'{gmi_stat}'}
                        self.geodata.update(new_geodata)
                    PageContentReader.CategoryGetter(ca_cat)

                elif ca_cat not in self.cats_to_ommit:
                    if all(cat not in ca_cat for cat in best_cats):
                        self.cats_to_ommit.append(ca_cat)
                    self.CategoryGetter(ca_cat)
            else:
                return

    def ReadAsList(self, page_title: str):
        items_list = []
        page = pywikibot.Page(Geolocbot.Site, page_title)
        items = page.text
        try:
            items = items[
                    items.index(self.items_list_openning_tag) +
                    len(self.items_list_openning_tag):items.index(self.items_list_closing_tag)
                    ]
        except ValueError:
            items = items
        list_bullet = config['wiki']['work-list']['bullet']
        number_of_lines = items.count(list_bullet)
        for line_number in range(number_of_lines):
            line = items[items.index(list_bullet):items.index('\n') + 1]
            if '[[' in line and ']]' in line:
                item = ' '.join(line[line.index('[[') + 2:line.index(']]')].split())
                items_list.append(item)
            else:
                raise PageUnpropperlyFormatted('brak linku wewnętrznego (nawiasów kwadratowych - [[, ]]) '
                                               f'w linii {line_number + 1} listy')
            items = items.replace(line, '')
        return items_list

    pass


class ExceptionSnitch(Geolocbot):
    """
    Class reporting bug-type Exceptions on a page set in config and outputting all Exceptions in console.
    """
    def __init__(self, exc_info):
        self.exc = exc_info
        self.bug_info_dest = config['wiki']['report']['bugs']
        self.not_bugs = ['TooManyArgs',
                         'PageDoesNotExist',
                         'PageUnpropperlyFormatted',
                         'WikidataItemNotFound',
                         'LabelsDoNotMatch',
                         'KeyError',
                         'ValueError']
        # TODO: finish urls
        self.bug_report_page = pywikibot.Page(self.Site, config['wiki']['report']['bugs'])
        self.bug_report_page_url = self.bug_report_page.title(as_url=1)
        self.tma_hint_page = pywikibot.Page(self.Site, config['wiki']['report']['toomanyargs-hints'])
        self.tma_hint_page_url = self.tma_hint_page.title(as_url=1)
        self.tma_report_page = pywikibot.Page(self.Site, config['wiki']['report']['toomanyargs-log'])
        self.tma_report_page_url = self.tma_report_page.title(as_url=1)
        self.SmartExceptionRelay()

    def SmartExceptionRelay(self):
        if self.exc['name'] == 'SystemExit':
            exit('Zatrzymano\n{0}[{1}]'.format(self.exc['msg'], strftime('%H:%M:%S')))

        if self.exc['name'] not in self.not_bugs:
            print(f"{self.exc['name']}: Oops! Nastąpił nieprzewidziany błąd programu. Zostanie on zgłoszony "
                  f"autorowi na stronie pod adresem {self.bug_report_page_url}.", file=sys.stderr)
            if config['interface']['tracebacks']:
                tbb = 'Traceback (most recent call last):\n'
                print(f"Traceback dla wyjątku:\n{self.exc['tb'].replace(tbb, '', 1)}", file=sys.stderr)
            self.Snitch(bug=True)
        elif self.exc['name'] == 'TooManyArgs':
            print(f"{self.exc['name']}: Nastąpił przewidziany błąd TooManyArgs. Uniemożliwia on pracę bota nad "
                  f"artykułem {Geolocbot.CurrentQuery} i zostanie zgłoszony autorowi na stronie pod adresem "
                  f"{self.tma_report_page.title(as_url=1)}, co umożliwi sformułowanie wskazówki na stronie pod adresem "
                  f"{self.tma_hint_page.title(as_url=1)}.\nOtrzymane argumenty: \n", file=sys.stderr)
            self.Snitch(bug=False, tma=True)
        else:
            print(f"{self.exc['name']}: {self.exc['msg']}", file=sys.stderr)
            if config['interface']['tracebacks']:
                tbb = 'Traceback (most recent call last):\n'
                print(f"Traceback dla wyjątku:\n{self.exc['tb'].replace(tbb, '', 1)}", file=sys.stderr)

    def Snitch(self, bug=True, tma=False):
        if bug:
            text = self.bug_report_page.text
            bug_id = text.count('|-')
            try:
                put_place = text.index('|}')
            except ValueError as valueerror:
                raise PageUnpropperlyFormatted(
                    "'|}' - koniec tabeli - nie występuje w treści strony. [ValueError: %s]" % valueerror
                )
            tb = self.exc['tb']
            if tb in text:
                same_bug_rep_part = text[:text.index(tb)]
                same_bug_rep_part = same_bug_rep_part[same_bug_rep_part.rindex('|-\n') + 2:]
                prev_bug_id = same_bug_rep_part[same_bug_rep_part.index('\n| ') + 3:]
                prev_bug_id = int(prev_bug_id[:prev_bug_id.index(' || ')])
                tb = 'Patrz traceback ID %s.' % prev_bug_id

            rep = "| %s || %s || " "<pre>%s</pre> || %s || {{/p}}\n|-\n" % (bug_id, self.exc['name'], tb,
                                                                            strftime('%d-%m-%Y %H:%M:%S'))
            self.bug_report_page.text = text[:put_place] + rep + text[put_place:]
            try:
                self.bug_report_page.save(u'/* Zgłaszam */ krytyczny wyjątek %s' % self.exc['name'], quiet=True)
                print('Błąd został zgłoszony.', file=sys.stderr)
            except:
                print('Nie udało się zgłosić błędu. Proszę, '
                      'skontaktuj się z autorem na tej stronie: https://nonsa.pl/wiki/Dyskusja_użytkownika:Stim',
                      file=sys.stderr)
                return
        elif tma:
            # TODO tma support
            pass
        return

    pass


class GeolocbotException(Exception):
    """
    Base class for new Exceptions occuring whilst the work of Geolocbot.
    """
    pass


class TooManyArgs(GeolocbotException):
    """
    Raised when expected only one argument as a result of a Geolocbot operation.
    """
    pass


class PageDoesNotExist(GeolocbotException):
    """
    Raised when the specified Page does not exist in Wiki set in Geolocbot config.
    """
    pass


class PageUnpropperlyFormatted(GeolocbotException):
    """
    Raised when Geolocbot PageContentReader could not process a Worklistpage with success because of formatting.
    """
    pass


class WikidataItemNotFound(GeolocbotException):
    """
    Raised when SPARQL query run towards Wikidata does not return QID.
    Usually means that the filtering data does not occure in the searched Wikidata item.
    """
    pass


class LabelsDoNotMatch(GeolocbotException):
    """
    Raised when despite success of SPARQL query the Wikidata item has different label than WikiArticle.
    """
    pass


class Locality(Geolocbot):
    """
    Basic class for a locality as a set of data.
    """
    pass


PageContentReader = PageContentReader()
UserQuery = UserQuery()

if __name__ == '__main__':
    while True:
        Geolocbot.run()
