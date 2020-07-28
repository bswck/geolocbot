import pywikibot


class WikiArticle(object):
    def __init__(self, title):
        self.pgTitle: str = title
        self.dbTitle: str = self._has_db_name()
        self.categories: list = self._is_in_categories()
        self.isDistrictType: bool = False
        self.teritorialInfo: dict = {}
        self.site: pywikibot.Site = pywikibot.Site('pl', 'nonsensopedia')

        self._adjectiveCategory: str
        self._adjectiveCategories: list
        self._beCareful: list
        self._categoriesLen: int
        self._page = pywikibot.Page(self.site, self.dbTitle)
        self._text: str = self._page.text

    def _has_db_name(self):
        if self.pgTitle.find(':') != -1:
            index_to_delete_from = ''

            for char in self.pgTitle:

                if char == ':':
                    index_to_delete_from = self.pgTitle.find(char) + 1

            self.dbTitle = str(self.pgTitle[index_to_delete_from::])
            self._has_db_name()

        self.dbTitle = self.dbTitle[0].upper() + self.dbTitle[1::]

        if self._page.isRedirectPage():
            self.dbTitle = str(self._page.getRedirectTarget()).replace('[[', '') \
                .replace(']]', '') \
                .replace('nonsensopedia:', '') \
                .replace('pl:', '')

            if '#' in self.dbTitle:
                for char in self.dbTitle:

                    if char == '#':
                        sharp_index = self.dbTitle.find(char)
                        self.dbTitle = self.dbTitle[:sharp_index]

        return self.dbTitle

    def _is_in_categories(self, pg_title):
         article_categories = [
                cat.title()
                for cat in pywikibot.Page(self.site, pg_title).categories()
                if 'hidden' not in cat.categoryinfo
         ]

        self._has_teritorial_info()

    def _has_teritorial_info(self, article_categories, pg_title):
        for i in range(len(article_categories)):
            page = pywikibot.Page(self.site, pg_title)
            text = page.text

            if "osiedl" in text[:250] or "dzielnic" in text[:250]:
                self.isDistrictType = True

            if 'gmina' not in self.teritorialInfo and "Kategoria:Gmina " in article_categories[i]:
                gmina = article_categories[i].replace("Kategoria:Gmina ", "")  # (No need for namespace and type name).
                self._is_in_categories(article_categories[i])
                add = {"gmina": gmina}
                self.teritorialInfo.update(add)

            elif 'powiat' not in self.teritorialInfo and "Kategoria:Powiat " in article_categories[i]:
                powiat = article_categories[i].replace("Kategoria:Powiat ", "")
                self._is_in_categories(article_categories[i])
                add = {"powiat": powiat.lower()}
                self.teritorialInfo.update(add)

            elif 'województwo' not in self.teritorialInfo and "Kategoria:Województwo " in article_categories[i]:
                wojewodztwo = article_categories[i].replace("Kategoria:Województwo ", "")
                add = {"województwo": wojewodztwo.upper()}
                self.teritorialInfo.update(add)

            elif "Kategoria:Ujednoznacznienia" in article_categories[i]:
                raise ValueError('Podana strona to ujednoznacznienie.')

            elif ("Kategoria:Miasta w" in article_categories[i] or "Kategoria:Powiaty w" in article_categories[
                i] or "Kategoria:Gminy w" in article_categories[i] or
                  "Kategoria:" + title in article_categories[i]) and (
                    'powiat' not in self.teritorialInfo or 'gmina' not in self.teritorialInfo):

                if geolocbotDatabases.check_status('powiat', title) is not False:
                    powiat = geolocbotDatabases.check_status('powiat', title)
                    add = {"powiat": powiat}
                    self.teritorialInfo.update(add)

                if geolocbotDatabases.check_status('gmina', title) is not False:
                    gmina = geolocbotDatabases.check_status('gmina', title)
                    add = {"gmina": gmina}
                    self.teritorialInfo.update(add)

                self._is_in_categories(article_categories[i])

            else:
                if article_categories[i] not in self.be_careful:
                    self.be_careful.append(article_categories[i])
                    self._is_in_categories(article_categories[i])

    def __str__(self):
        return self.pgTitle


class Databases(WikiArticle):
    def __init__(self):
        import pandas
        self.TercDb = pandas.read_csv("SIMC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ_GMI', 'NAZWA', 'SYM'])
        self.SimcDb = pandas.read_csv("TERC.csv", sep=';', usecols=['WOJ', 'POW', 'GMI', 'RODZ', 'NAZWA', 'NAZWA_DOD'])

    def check_status(self, t: str, nm: str):
        if t == 'gmina':
            gmina = self.TercDb.loc[(self.TercDb['NAZWA'] == super().dbTitle) &
                                    ((self.TercDb['NAZWA_DOD'] == 'gmina miejska') |
                                     (self.TercDb['NAZWA_DOD'] == 'obszar wiejski') |
                                     (self.TercDb['NAZWA_DOD'] == 'gmina wiejska') |
                                     (self.TercDb['NAZWA_DOD'] == 'gmina miejsko-wiejska'))]

            if gmina.empty:
                return False

            else:
                gmina = gmina.reset_index()
                return gmina.at[0, 'NAZWA']

        elif t == 'powiat':
            powiat = self.TercDb.loc[(self.TercDb['NAZWA'] == nm) & (
                    (self.TercDb['NAZWA_DOD'] == t) | (self.TercDb['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

            if powiat.empty:
                return False

            else:
                powiat = powiat.reset_index()
                return powiat.at[0, 'NAZWA']

        else:
            target = self.TercDb.loc[(self.TercDb['NAZWA'] == nm) & (
                    (self.TercDb['NAZWA_DOD'] == 'powiat') | (
                     self.TercDb['NAZWA_DOD'] == 'miasto na prawach powiatu'))]

            if not target.empty:
                target = target.reset_index()
                terc_id_shortened = str(target.at[0, 'WOJ']).zfill(2) + str(int(float(str(target.at[0, 'POW'])))).zfill(
                    2)
                return terc_id_shortened

            else:
                target = self.TercDb.loc[(self.TercDb['NAZWA'] == nm.upper()) &
                                         (self.TercDb['NAZWA_DOD'] == 'województwo')]

                if not target.empty:
                    terc_id_shortened = str(target.at[0, 'WOJ']).zfill(2)
                    return terc_id_shortened

                else:
                    return False
