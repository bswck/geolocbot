# Geolocbot
The **Geolocbot** is a bot that uses [geolocation template](https://nonsa.pl/wiki/Szablon:Lokalizacja) 
to add coordinates and TERYT identifiers to articles about Polish localities and link them to Wikidata 
items that are the source of those coordinates.

## Usage

Change the working directory to the home directory of 
[pywikibot framework](https://github.com/wikimedia/pywikibot).

``$ cd ~/pywikibot``

Run on "Junikowo" page:

``$ python pwb.py geolocbot/bot --page Junikowo``

Run on "Kategoria:CustomCat" category:

``$ python pwb.py geolocbot/bot --cat CustomCat`` or  
``$ python pwb.py geolocbot/bot --cat Kategoria:CustomCat``

Run on "Kategoria:CustomCat" category forever:

``$ python pwb.py geolocbot/bot --cat CustomCat --sleepless``

Run on default category forever:

``$ python pwb.py geolocbot/bot --sleepless``

You cannot run the bot on a single page forever.

## Error handling

If an error occurs whilst running, its traceback is outputted in console. If it happens whilst processing
a specified page, bot erases geolocation template from it and report it on deferment page you can set by
passing argument `--deferpage`.

## Author

(C) Stim, 2020
