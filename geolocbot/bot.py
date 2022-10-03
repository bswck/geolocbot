from __future__ import annotations

import argparse
import glob
import os
import string
import typing

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators

from geolocbot import config
from geolocbot.location import WikidataLocationSearch
from geolocbot.teryt import TERYTSearch
from geolocbot.scraper import scrape_subdivisions

if typing.TYPE_CHECKING:
    from typing import Iterable

    from geolocbot.teryt import TERYT
    from geolocbot.location import WikidataLocation


class GeolocationBot(
    pywikibot.bot.SingleSiteBot,
    pywikibot.bot.ConfigParserBot,
):
    INI: str = config.CONFIG_FILENAME

    verbose: bool = config.VERBOSE
    param_metadata: dict[str, str] = config.PARAM_METADATA
    template_name: str = config.TEMPLATE_NAME
    replace_template_name: str = config.REPLACE_TEMPLATE_NAME
    summary_template: string.Template = string.Template(config.SUMMARY_TEMPLATE)

    fam: pywikibot.Family = config.FAMILY
    site: pywikibot.APISite = pywikibot.Site(code=list(fam.langs)[0], fam=fam)

    generator_category: pywikibot.Category = pywikibot.Category(
        site, config.GENERATOR_CATEGORY
    )
    generator: Iterable[pywikibot.Page] = pagegenerators.CategorizedPageGenerator(
        generator_category
    )

    teryt: TERYTSearch = TERYTSearch()
    wikidata: WikidataLocationSearch = WikidataLocationSearch()

    def setup(self) -> None:
        """
        This method is called before the bot starts processing pages.

        It is used to log in to the wiki and Wikidata and load the latest TERYT datasets.
        """

        if not self.site.username():
            raise ValueError(
                "Please provide the target wiki username in the environment variable WIKI_LOGIN."
            )
        self.site.login()

        if (
            not self.wikidata.site.username()
        ):  # rare, but what if it's set to an empty string?...
            raise ValueError(
                "Please provide the target wiki username "
                "in the environment variable WIKIDATA_LOGIN."
            )
        self.wikidata.site.login()

        directory = os.path.abspath(
            os.getenv("TERYT_DATA_DIR", "geolocbot/teryt_datasets")
        )
        registry_files = {
            "NTS": max(glob.glob(f"{directory}/NTS*.csv")),
            "SIMC": max(glob.glob(f"{directory}/SIMC*.csv")),
            "TERC": max(glob.glob(f"{directory}/TERC*.csv")),
            "WMRODZ": max(glob.glob(f"{directory}/WMRODZ*.csv")),
        }
        for code, filename in registry_files.items():
            self.teryt.load_registry(
                code,
                os.path.join(directory, filename),
                fmt=filename.rsplit(".", 1)[-1],
                sep=";",
            )
        self.teryt.memoize_rm()

    def skip_page(self, page: pywikibot.Page) -> bool:
        """Check if page can be skipped. We operate on existing pages only."""
        return not page.exists()

    def parametrize_template(
        self,
        teryt: TERYT,
        location: WikidataLocation,
        template: mwparserfromhell.nodes.Template | None = None,
    ) -> str:
        """
        Parametrize the template used by the bot with the location and TERYT data.
        """
        if template is None:
            template = mwparserfromhell.nodes.Template(self.template_name)
        if location.lat:
            location_value = f"{location.lat:.6f}, {location.lon:.6f}"
        else:
            location_value = None
        for template_param, value in dict(
            location=location_value,
            wikidata=location.wikidata,
            simc=teryt.simc.get_wd_key(),
            terc=teryt.terc.get_wd_key(),
        ).items():
            try:
                template.remove(template_param)
            except ValueError:
                pass
            if value:
                param = self.param_metadata[template_param]
                template.add(param, value)
        template.name = self.template_name
        return str(template)

    def update_page(
        self, page: pywikibot.Page, teryt: TERYT, location: WikidataLocation
    ) -> None:
        """
        Update the page with the template containing the location and TERYT data.

        For Nonsensopedia, the target template will be {{stopka}}
        and the replacement template will be {{lokalizacja}}.

        If there is no target template (or replacement template), the template is added before
        the first category ([[Category:...]]). If there are no categories, the template is added
        at the end of the page.
        If the target template is already present, it's simply updated in the text.
        If there is a replacement template used, it's replaced with the target template
        containing the location and TERYT data.
        If both target template and replacement templates are present, the target template
        is updated and every other template is removed.
        """
        text = mwparserfromhell.parse(page.text)
        templates = text.filter(
            matches=lambda template_node: (
                str(template_node.name)
                in {self.replace_template_name, self.template_name}
            ),
            forcetype=mwparserfromhell.nodes.Template,
        )
        if templates:
            templates = sorted(
                templates,
                key=lambda template_node: template_node == self.replace_template_name,
            )
            template = templates[0]
            for left_template in templates[1:]:
                text.remove(left_template)
        else:
            template = mwparserfromhell.nodes.Template(self.template_name)
        parametrized_template = self.parametrize_template(
            template=template, teryt=teryt, location=location
        )
        if templates:
            text.replace(template, parametrized_template)
        else:
            category_nodes = text.filter(
                matches=lambda link: (
                    pywikibot.Page(self.site, link.title).is_categorypage()
                    and not link.title.startswith(":")
                ),
                forcetype=mwparserfromhell.nodes.Wikilink,
            )
            first_category = category_nodes[0] if category_nodes else None
            if first_category:
                text.insert_before(first_category, parametrized_template)
            else:
                text.append(parametrized_template)
        page.text = str(text)

    def get_summary(self, teryt: TERYT, location: WikidataLocation) -> str:
        """Generate the edit summary."""
        extra = dict(
            wikidata=location.wikidata,
            simc=teryt.simc.get_wd_key(),
            terc=teryt.terc.get_wd_key(),
        )
        return self.summary_template.safe_substitute(
            page_name=teryt.sub.page_name,
            lat=location.lat or "?",
            lon=location.lon or "?",
            extra=", ".join(
                f"{key!s}={value!s}" for key, value in extra.items() if value
            ),
        )

    def report(self, page, location, teryt) -> None:
        """Report the result of the operation on an article."""
        if not self.verbose:
            return
        msg = page.title()
        if location:
            msg += f" - {location}"
            for item in filter(None, teryt[1:]):
                wd_key = item.get_wd_key()
                if wd_key:
                    msg += "\n  " + item.registry_name + " = " + wd_key
        else:
            msg += " - no location found"
        pywikibot.info(msg)

    def treat(self, page) -> None:
        """Process a single page."""
        subdivisions = scrape_subdivisions(page)
        teryt = self.teryt.search(subdivisions)
        location = self.wikidata.search(teryt)
        self.report(page, location, teryt)
        if location:
            self.update_page(page, teryt=teryt, location=location)
            page.save(summary=self.get_summary(teryt, location), quiet=not self.verbose)


if __name__ == "__main__":
    geolocbot = GeolocationBot()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--page", nargs="?", default=None, help="Single page to process."
    )
    parser.add_argument(
        "-v", "-verbose", action="store_true", help="Turn on verbose mode."
    )

    args = parser.parse_args()

    if args.page:
        geolocbot.setup()
        geolocbot.treat(pywikibot.Page(geolocbot.site, args.page))
    else:
        geolocbot.run()
