# Author: Stim, 2020.
# Geolocalisation bot for Nonsensopedia.
# License: GNU GPLv3.
import inspect
import types
from typing import cast
import pywikibot as pwbot
from __init__ import geolocbot
from databases import check_status

site = geolocbot.site  # we're on nonsa.pl

captured = {}
p = []
getcats_fors = []
be_careful = []


def cleanup_getcats():
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    if captured != {}:
        for key_value in list(captured.keys()):
            del captured[key_value]

    while p:
        del p[0]

    while getcats_fors:
        del getcats_fors[0]

    while be_careful:
        del be_careful[0]


# This function reviews a category and decides,
# whether it is needed or not.
def collect_information_from_categories(article_categories, title):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    for i in range(len(article_categories)):
        getcats_fors.append(str(len(getcats_fors) + 1))
        page = pwbot.Page(site, title)
        text = page.text

        if "osiedl" in text[:250] or "dzielnic" in text[:250]:
            if not p:
                print()
                geolocbot.output("-" * (73 // 2) + "UWAGA!" + "-" * ((73 // 2) + 1))
                geolocbot.output('(nonsa.pl) [TooManyRows]: Artykuł prawdopodobnie dotyczy osiedla lub dzielnicy.')
                geolocbot.output("-" * 79)
                print()
                p.append(' ')

        # Checks if the category contains "Gmina".
        if 'gmina' not in captured and "Kategoria:Gmina " in article_categories[i]:
            gmina = article_categories[i].replace("Kategoria:Gmina ", "")  # (No need for namespace and type name).
            raise_categories(article_categories[i])
            add = {"gmina": gmina}
            captured.update(add)

        # Checks if the category contains "Powiat "; disclaiming category "Powiaty".
        elif 'powiat' not in captured and "Kategoria:Powiat " in article_categories[i]:
            powiat = article_categories[i].replace("Kategoria:Powiat ", "")
            raise_categories(article_categories[i])
            add = {"powiat": powiat.lower()}
            captured.update(add)

        # Checks if the category contains "Województwo ".
        elif 'województwo' not in captured and "Kategoria:Województwo " in article_categories[i]:
            wojewodztwo = article_categories[i].replace("Kategoria:Województwo ", "")
            add = {"województwo": wojewodztwo.upper()}
            captured.update(add)

        # Exceptions.
        elif "Kategoria:Ujednoznacznienia" in article_categories[i]:
            raise ValueError('Podana strona to ujednoznacznienie. [b]')

        # Reading the category of category if it's one of these below.
        elif ("Kategoria:Miasta w" in article_categories[i] or "Kategoria:Powiaty w" in article_categories[
            i] or "Kategoria:Gminy w" in article_categories[i] or
              "Kategoria:" + title in article_categories[i]) and ('powiat' not in captured or 'gmina' not in captured):

            if check_status('powiat', title) is not False:
                powiat = check_status('powiat', title)
                add = {"powiat": powiat}
                captured.update(add)

            if check_status('gmina', title) is not False:
                gmina = check_status('gmina', title)
                add = {"gmina": gmina}
                captured.update(add)

            raise_categories(article_categories[i])

        else:
            if article_categories[i] not in be_careful:
                be_careful.append(article_categories[i])
                raise_categories(article_categories[i])


def raise_categories(title):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    article_categories = [
        cat.title()
        for cat in pwbot.Page(site, title).categories()
        if 'hidden' not in cat.categoryinfo
    ]

    collect_information_from_categories(article_categories, title)
    return article_categories


def run(title):
    geolocbot.debug.output(cast(types.FrameType, inspect.currentframe()).f_code.co_name)
    page = pwbot.Page(site, title)
    text = page.text

    if text == '':
        raise KeyError('Nie ma takiej strony. [b]')

    raise_categories(title)  # script starts
    geolocbot.output('Z kategorii artykułu mam następujące dane:')
    geolocbot.output('województwo: {0}.'.format(
        (captured['województwo'].lower() if 'województwo' in list(captured.keys()) else '–')))
    geolocbot.output('powiat: {0}.'.format((captured['powiat'] if 'powiat' in list(captured.keys()) else '–')))
    geolocbot.output('gmina: {0}.'.format((captured['gmina'] if 'gmina' in list(captured.keys()) else '–')))
    line = {"NAZWA": title}
    captured.update(line)
    return captured
