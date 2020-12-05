# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Geoloc-Bot. """

from geolocbot import *

# test
if __name__ == '__main__':
    def process_page(pagename):
        class NotFound:
            def __repr__(self):
                return '<not found>'
        loc = searching.wiki.terinfo(pagename)
        ts = dict(searching.teryt.transferred_searches(loc.name))
        simc, terc, nts = (ts.get(k.upper()) for k in searching.teryt.subsystems)
        ids = {'simc': simc.id, 'terc': terc.terid if terc else '', 'nts': nts.terid if nts else ''}
        try:
            coords = searching.wiki.data_repo.coords(loc.name, **ids)
            result = {'coords': coords, 'simc': simc.id, 'terc': terc.terid, 'nts': nts.terid}
        except (BaseException, Exception) as exception:
            output(f'{tools.TC.grey}(exception){tools.TC.r}', exception)
            result = NotFound()
        return result
