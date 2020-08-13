import pandas
import pywikibot


def import_dataframes():
    basic_cols = ['WOJ', 'POW', 'GMI', 'NAZWA']
    terc_db = pandas.read_csv('TERC.csv', sep=';', usecols=[*basic_cols, 'RODZ', 'NAZWA_DOD']).fillna(0)
    simc_db = pandas.read_csv('SIMC.csv', sep=';', usecols=[*basic_cols, 'RODZ_GMI', 'NAZWA', 'SYM'])
    simc_db = simc_db.fillna(0)
    nts_db = pandas.read_csv("NTS.csv", sep=';').fillna(0)
    dataframes = [simc_db, terc_db, nts_db]

    for db in dataframes:
        float_col = db.select_dtypes(include=['int64', 'float64'])
        for col in float_col.columns.values:
            db[col] = db[col].astype(float).astype(int).astype(str)
            zfill2_cols = ['WOJ', 'POW', 'GMI']
            for _col in zfill2_cols:
                db[_col] = db[_col].astype(str).str.zfill(2)

    simc_db['SYM'] = simc_db['SYM'].astype(str).str.zfill(7)
    return dataframes


databases = import_dataframes()


class Geolocbot(object):
    Site = pywikibot.Site('pl', 'nonsensopedia')
    pass


class Methods(Geolocbot):
    def __init__(self):
        super().__init__()
        self.cats_to_ommit = []
        self.geodata = {}

    @staticmethod
    def care_about_status(locality_name, status=None):
        terc_db = databases[1]
        locality_name = Methods.DbTitle(locality_name)
        if status == 'gmina':
            gmina_values = ['gmina miejska', 'gmina wiejska', 'gmina miejsko-wiejska', 'obszar wiejski']
            gmina = terc_db.loc[(terc_db['NAZWA'] == locality_name) &
                                (terc_db['NAZWA_DOD'].str.contains('|'.join(gmina_values), regex=True))]
            if gmina.empty:
                return False
            else:
                gmina = gmina.reset_index()
                return gmina.at[0, 'NAZWA']
        elif status == 'powiat':
            powiat_values = ['powiat', 'na prawach powiatu']
            powiat = terc_db.loc[(terc_db['NAZWA'] == locality_name) &
                                 (terc_db['NAZWA_DOD'].str.contains('|'.join(powiat_values), regex=True))]
            if powiat.empty:
                return False
            else:
                powiat = powiat.reset_index()
                return powiat.at[0, 'NAZWA']
        else:
            target = Methods.care_about_status(locality_name, status='powiat')
            if target is False:
                target = terc_db.loc[(terc_db['NAZWA'] == locality_name.upper()) &
                                     (terc_db['NAZWA_DOD'] == 'województwo')]
                if not target.empty:
                    terc_id_shortened = target.at[0, 'WOJ']
                    return terc_id_shortened
                else:
                    return False

            else:
                target = target.reset_index()
                terc_id_shortened = f"{target.at[0, 'WOJ']}{target.at[0, 'POW']}"
                return terc_id_shortened

    @staticmethod
    def Title(title: str):
        s = Geolocbot.Site
        # Delete namespace
        title = title[title.index(':') + 1::] if ':' in title else title
        # First letter uppercase
        title = title.title()
        _pg = pywikibot.Page(s, title)
        # Check for redir
        if _pg.isRedirectPage():
            title = _pg.getRedirectTarget().replace(f'[[{s.family.name}:{s.code}:', '').replace(']]', '')
            title = title[:title.index('#')] if '#' in title else title
        return title

    @staticmethod
    def DbTitle(title: str):
        title = title[:title.index(' (')] if ' (' in title else title
        return title

    def CategoryReader(self, pg_title):
        article_categories = [
            cat.title() for cat in pywikibot.Page(self.Site, pg_title).categories()
            if 'hidden' not in cat.categoryinfo
        ]
        Methods.GeoDataSelector(article_categories, pg_title)
        return article_categories

    def GeoDataSelector(self, article_categories, pg_title):
        for i in range(len(article_categories)):
            print(f'{article_categories[i]}')
            page = pywikibot.Page(self.Site, pg_title)
            text = page.text
            district_signs = ['osiedl', 'dzielnic', 'częścią', 'część']
            teritorial_parts = ['GMI', 'POW', 'WOJ']
            cat_teritorial_parts = ['Kategoria:Gmina ', 'Kategoria:Powiat ', 'Kategoria:Województwo ']
            skip_cats = ['Kategoria:Miasta w', 'Kategoria:Powiaty w', 'Kategoria:Gminy w',
                         f'Kategoria:{pg_title}']

            if any(district_sign in text[:250] for district_sign in district_signs):
                WikiArticle.IsDistrict = True

            for _i in range(3):
                if teritorial_parts[_i] not in self.geodata and cat_teritorial_parts[_i] in article_categories[i]:
                    value = Methods.DbTitle(article_categories[i].replace(cat_teritorial_parts[_i], ''))
                    info = {teritorial_parts[_i]: (value.lower()
                                                   if teritorial_parts[_i] != 'WOJ'
                                                   else value.upper())}
                    self.geodata.update(info)

            if 'Kategoria:Ujednoznacznienia' in article_categories[i]:
                raise ValueError('Podana strona to ujednoznacznienie.')

            elif any(cat in article_categories[i] for cat in skip_cats) and all(
                    tp not in self.geodata for tp in teritorial_parts):
                pow_stat = Methods.care_about_status(pg_title, status='powiat')
                gmi_stat = Methods.care_about_status(pg_title, status='gmina')
                if pow_stat is not False:
                    new_geodata = {'POW': f'{pow_stat}'}
                    self.geodata.update(new_geodata)
                if gmi_stat is not False:
                    new_geodata = {'GMI': f'{gmi_stat}'}
                    self.geodata.update(new_geodata)
                Methods.CategoryReader(article_categories[i])

            elif article_categories[i] not in self.cats_to_ommit:
                self.cats_to_ommit.append(article_categories[i])
                self.CategoryReader(article_categories[i])


class WikiArticle(Geolocbot):
    def __init__(self, page_title: str):
        super().__init__()
        self._T = page_title
        self.Page = pywikibot.Page(self.Site, self.Title)
        self.Categories = []
        self.GeoData = {}

    def get(self):
        self.Categories = self._Categories()
        self.GeoData = Methods.geodata
        return self.GeoData

    @property
    def Title(self):
        return Methods.Title(self._T)

    @property
    def DbTitle(self):
        return Methods.DbTitle(self.Title)

    def _Categories(self):
        return Methods.CategoryReader(self.Title)

    def __str__(self):
        return self.Title


class DatabaseSearch(Geolocbot):
    def __init__(self, loctitle):
        self.Title = Methods.DbTitle(loctitle)

    def AsTERC(self, geodata: dict):
        asterc = {}
        encode_cols = geodata.keys()
        terc_db = databases[0]
        for col in encode_cols:
            terc_id = {col: terc_db.loc[(terc_db['NAZWA'] == self.Title) & (terc_db[col] == geodata[col])]}
            asterc.update(terc_id)
        return asterc


class WikidataSearch(Geolocbot):
    def __init__(self):
        pass


DatabaseSearch = DatabaseSearch()
Methods = Methods()

print(f"\n{WikiArticle('Warszawa').get()};")
