import pandas
import pywikibot


class Geolocbot(object):
    def __init__(self):
        self.Site = pywikibot.Site('pl', 'nonsensopedia')
        Methods.import_dataframes()

    def run(self):
        pass


class Methods(Geolocbot):
    def __init__(self):
        super().__init__()
        self.cats_done = []

    @staticmethod
    def import_dataframes():
        basic_cols = ['WOJ', 'POW', 'GMI', 'NAZWA']
        terc_db = pandas.read_csv('TERC.csv', sep=';', usecols=[*basic_cols, 'RODZ', 'NAZWA_DOD']).fillna(0)
        simc_db = pandas.read_csv('SIMC.csv', sep=';', usecols=[*basic_cols, 'RODZ_GMI', 'NAZWA', 'SYM'])
        simc_db = simc_db.fillna(0)
        nts_db = pandas.read_csv("NTS.csv", sep=';').fillna(0)
        databases = [terc_db, simc_db, nts_db]

        for db in databases:
            float_col = db.select_dtypes(include=['float64'])
            for col in float_col.columns.values:
                db[col] = db[col].astype(float)
                db[col] = db[col].astype(int)
                db[col] = db[col].astype(str)
                zfill2_cols = ['WOJ', 'POW', 'GMI']
                for _col in zfill2_cols:
                    db[_col] = db[_col].astype(str).str.zfill(2)

        Geolocbot.terc_db = terc_db
        Geolocbot.simc_db = simc_db
        Geolocbot.nts_db = nts_db

    @staticmethod
    def care_about_status(locality_name, status=None):
        if status == 'gmina':
            gmina = terc_database.loc[(terc_database['NAZWA'] == locality_name) &
                                      ((terc_database['NAZWA_DOD'] == 'gmina miejska') |
                                       (terc_database['NAZWA_DOD'] == 'obszar wiejski') |
                                       (terc_database['NAZWA_DOD'] == 'gmina wiejska') |
                                       (terc_database['NAZWA_DOD'] == 'gmina miejsko-wiejska'))]
            if gmina.empty:
                return False
            else:
                gmina = gmina.reset_index()
                return gmina.at[0, 'NAZWA']
        elif status == 'powiat':
            powiat = terc_database.loc[(terc_database['NAZWA'] == locality_name) & (
                    (terc_database['NAZWA_DOD'] == status) |
                    (terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu'))]
            if powiat.empty:
                return False
            else:
                powiat = powiat.reset_index()
                return powiat.at[0, 'NAZWA']
        else:
            target = terc_database.loc[(terc_database['NAZWA'] == locality_name) & (
                    (terc_database['NAZWA_DOD'] == 'powiat') | (
                     terc_database['NAZWA_DOD'] == 'miasto na prawach powiatu'))]
            if not target.empty:
                target = target.reset_index()
                terc_id_shortened = f"{target.at[0, 'WOJ']}".zfill(2) + f"{target.at[0, 'POW']}".zfill(2)
                return terc_id_shortened
            else:
                target = terc_database.loc[(terc_database['NAZWA'] == locality_name.upper()) &
                                           (terc_database['NAZWA_DOD'] == 'województwo')]
                if not target.empty:
                    terc_id_shortened = str(target.at[0, 'WOJ']).zfill(2)
                    return terc_id_shortened
                else:
                    return False

    def ReadCategories(self, pg_title):
        article_categories = [
            cat.title()
            for cat in pywikibot.Page(self.Site, pg_title).categories()
            if 'hidden' not in cat.categoryinfo
        ]
        Methods.CategoryFilter(article_categories, pg_title)
        return article_categories

    def CategoryFilter(self, article_categories, pg_title):
        for i in range(len(article_categories)):
            page = pywikibot.Page(self.Site, pg_title)
            text = page.text
            district_signs = ['osiedl', 'dzielnic', 'części', 'część']
            teritorial_parts = ['gmina', 'powiat', 'województwo']
            cat_teritorial_parts = ['Kategoria:Gmina', 'Kategoria:Powiat', 'Kategoria:Województwo']
            skip_cats = ['Kategoria:Miasta w', 'Kategoria:Powiaty w', 'Kategoria:Gminy w',
                         f'Kategoria:{pg_title}']

            if any(district_sign in text[:250] for district_sign in district_signs):
                WikiArticle.IsDistrict = True

            for _i in range(3):
                if teritorial_parts[_i] not in WikiArticle.Info and cat_teritorial_parts[_i] in article_categories[i]:
                    value = article_categories[i].replace(cat_teritorial_parts[_i], '')
                    info = {teritorial_parts[_i]: (value.lower()
                                                   if teritorial_parts[_i] != 'województwo'
                                                   else value.upper())}
                    self._Info.update(info)

            if 'Kategoria:Ujednoznacznienia' in article_categories[i]:
                raise ValueError('Podana strona to ujednoznacznienie.')

            elif any(cat in article_categories[i] for cat in skip_cats) and all(
                    tp not in WikiArticle.Info for tp in teritorial_parts):
                if Methods.care_about_status('powiat', pg_title):
                    new_info = {'powiat': '%s' % Methods.care_about_status('powiat', pg_title)}
                    WikiArticle.Info.update(new_info)
                elif Methods.care_about_status('gmina', pg_title):
                    new_info = {'gmina': '%s' % Methods.care_about_status('gmina', pg_title)}
                    WikiArticle.Info.update(new_info)
                Methods.ReadCategories(pg_title)

            elif article_categories[i] not in Methods.cats_done:
                Methods.cats_done.append(article_categories[i])
                Methods.ReadCategories(article_categories[i])


class WikiArticle(Geolocbot):
    def __init__(self, page_title: str):
        super().__init__()
        self.Title = self._Title(page_title)
        self.Page = pywikibot.Page(self.Site, self.Title)
        self.DbTitle = self._DbTitle(self.Title)
        self.Info = self._Categories()

    def _Title(self, title: str):
        # Delete namespace
        title = title[title.index(':') + 1::] if ':' in title else title
        # Capitalize
        title = title[0].upper() + title[1::]
        _pg = pywikibot.Page(self.Site, title)
        # Check for redir
        is_redir = _pg.isRedirectPage()
        if is_redir:
            title = _pg.getRedirectTarget().replace('[[nonsensopedia:pl:', '').replace(']]', '')
            title = title[:title.index('#')] if '#' in title else title
        return title

    @staticmethod
    def _DbTitle(title: str):
        title = title[:title.index(' (')] if ' (' in title else title
        return title

    def _Categories(self):
        return Methods.ReadCategories(self.Title)

    def __str__(self):
        return self.Title

Methods = Methods()

print(f"{WikiArticle('Borki (Opole)')};")

