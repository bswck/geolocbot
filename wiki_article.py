import pywikibot
# import pandas
from tools import *


class WikiArticle(object):
    def __init__(self, page_title: str):
        self.Site = pywikibot.Site('pl', 'nonsensopedia')
        self.Title = self._Title(page_title)
        self.Page = pywikibot.Page(self.Site, self.Title)
        self.DbTitle = self._DbTitle(self.Title)
        self.Categories = self._Categories()

    def _Title(self, title: str):
        # Delete namespace
        title = title[title.index(':') + 1::] if ':' in title else title
        # Capitalize
        title = title[0].upper() + title[1::]
        _pg = pywikibot.Page(self.Site, title)
        # Check for redir
        is_redir = _pg.isRedirectPage()
        if is_redir:
            title = mass_remove(_pg.getRedirectTarget(), '[[', 'nonsensopedia:', 'pl:', ']]')
            title = title[:title.index('#')] if '#' in title else title
        return title

    @staticmethod
    def _DbTitle(title: str):
        title = title[:title.index(' (')] if ' (' in title else title
        return title

    def _Categories(self):
        def Read(pg_title):
            article_categories = [
                cat.title()
                for cat in pwbot.Page(site, page_name).categories()
                if 'hidden' not in cat.categoryinfo
            ]
            Compare(article_categories, pg_title)
            return article_categories

        def Compare(article_categories, pg_title):
            for once in range(len(article_categories)):
                page = pywikibot.Page(WikiArticle.Site, pg_title)
                text = page.text

                if are('osiedl', 'dzielnic', inside=text[:250]):


    def __str__(self):
        return self.Title


print(f"{WikiArticle('Borki (Opole)')};")
