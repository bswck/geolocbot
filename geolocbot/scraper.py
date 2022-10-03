from __future__ import annotations

import collections
import re

import pywikibot
from pywikibot.backports import removeprefix


Subdivisions = collections.namedtuple("Subdivisions", "page_name name gmi pow woj")


class SubdivisionScraper:
    SUBDIVISION_CATEGORY: str = (
        "("
        r"Województwo (?P<woj>.+)|"
        r"Powiat (?P<pow>.+)( ?\(województwo (?P<woj_disambig>.+)\))?|"
        r"Gmina (?P<gmi>.+)( ?\(powiat (?P<pow_disambig>.+)\))?|"
        "%(name)s|"
        "(?P<meta>.+) w województwie (.+)"
        ")"
    )

    POWIAT_SINGULAR: str = "Powiat"
    POWIAT_PLURAL: str = "Powiaty"
    WOJ_DISAMBIG: re.Pattern = re.compile(
        r"([^(]+)( ?\((województwo (?P<woj>.+)|powiat (?P<pow>.+))\))?", flags=re.I
    )

    def __init__(self, page: pywikibot.Page) -> None:
        self.page = page
        self.page_name = page.title(with_ns=False, with_section=False)
        subdivisions = Subdivisions(
            page_name=self.page_name,
            name=page.title(with_ns=False, with_section=False, without_brackets=True),
            gmi=None,
            pow=None,
            woj=None,
        )

        woj_disambig = self.WOJ_DISAMBIG.match(self.page_name)
        if woj_disambig:
            subdivisions = subdivisions._replace(**woj_disambig.groupdict())
        self.subdivisions = subdivisions
        self.category_queue = collections.deque()

    def normalize_subdivisions(self) -> None:
        """
        Normalize subdivision data to the form that it can be used to search TERYT.
        Voivodships in TERC are uppercase, so we need to uppercase them.
        """
        subdivisions = self.subdivisions
        if subdivisions.woj:
            self.subdivisions = subdivisions._replace(woj=subdivisions.woj.upper())  # type: ignore

    def traverse_categories(
        self, page: pywikibot.Page, page_name: str | None = None
    ) -> None:
        """Traverse categories to find the subdivision data."""
        if page_name is None:
            page_name = page.title(with_ns=False, with_section=False)
        category_pat = re.compile(
            self.SUBDIVISION_CATEGORY % dict(name=re.escape(page_name)), flags=re.I
        )
        for subdivision_category in filter(
            None,
            map(
                lambda category: category_pat.match(
                    category.title(with_ns=False, with_section=False)
                ),
                page.categories(),
            ),
        ):
            scraped = subdivision_category.groupdict()
            scraped.setdefault("woj", scraped.pop("woj_disambig", None))
            scraped.setdefault("pow", scraped.pop("pow_disambig", None))
            if scraped.pop("meta", None) == self.POWIAT_PLURAL:
                scraped["pow"] = removeprefix(page_name, self.POWIAT_SINGULAR).strip()
            self.subdivisions = self.subdivisions._replace(
                **{key: value for key, value in scraped.items() if value}
            )
            category_name = subdivision_category.string
            if category_name in {self.subdivisions.name, self.page_name}:
                self.category_queue.appendleft(category_name)
            else:
                self.category_queue.append(category_name)

    def scrape_subdivisions(self) -> Subdivisions:
        """Scrape subdivision data from the page's categories."""
        self.traverse_categories(self.page, page_name=self.page_name)
        if not self.category_queue:
            self.category_queue = [
                category.title(with_ns=False, with_section=False)
                for category in self.page.categories()
            ]
        while not self.subdivisions.woj and self.category_queue:
            cur_queue = self.category_queue.copy()
            for category_name in cur_queue:
                category = pywikibot.Category(self.page.site, category_name)
                self.traverse_categories(category)
                if self.subdivisions.woj:
                    break
                self.category_queue.remove(category_name)
        self.normalize_subdivisions()
        return self.subdivisions


def scrape_subdivisions(page) -> Subdivisions:
    """Scrape subdivision data from the page name and from its categories."""
    return SubdivisionScraper(page).scrape_subdivisions()
