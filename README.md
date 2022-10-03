# Geolocbot

**Geolocbot** is a bot that uses the [footer template](https://nonsa.pl/wiki/Szablon:Stopka) 
to add coordinates and TERYT identifiers to articles about Polish localities and link them to Wikidata
items that are the source of those coordinates.

## Usage
Change the directory to the one where you cloned the repository, whatever is going to be done.
 
1. Install the requirements: `pip install -r requirements.txt`
2. Configure the bot by editing settings in the `geolocbot.conf` file. 

   The file should have the following structure:
   
   `[template]` section
   * `name` - name of the template to be used to add coordinates, Wikidata and TERYT identifiers.
   * `replace_template` - name of the template to replace (with the template named as specified 
      in the above option) if found. This could be for example some `{{needs_location}}` template.
   * `location_param` - name of the parameter storing the locality coordinates.
   * `wikidata_param` - name of the parameter storing the Wikidata item identifier.
   * `terc_param` - name of the parameter storing the TERC identifier.
   * `simc_param` - name of the parameter storing the SIMC identifier.

   `[geolocbot]` section
   * `generator_category` - category to used as a source of articles to be processed.
   * `summary_template` - summary string template to be used in the edit summary, for example 
     `Done with $page_name`.

3. Set environment variables `WIKI_LOGIN` and `WIKIDATA_LOGIN` for the authentication purposes.
   `WIKI_LOGIN` variable will be used to log in to the wiki, while `WIKIDATA_LOGIN` will be used to
   log in to Wikidata. `WIKIDATA_LOGIN` defaults to required `WIKI_LOGIN`.
   You will be prompted for passwords for both wiki accounts during first run and whenever 
   the pywikibot cookies expire (or are deleted).
4. Run the bot in standard manner with `python geolocbot/bot.py -v` (set `-v` flag for verbose output).
   Run the bot with `--page` flag to process a single page and then exit, 
   for example `python geolocbot/bot.py --page "Warszawa"`.


   `$ python geolocbot/bot.py -v`

   ```
   Pszczyna - WikidataLocation(lat=49.983333333333, lon=18.95, wikidata='Q948304')
     TERC = 2410054
     SIMC = 0942222
     NTS = 2243310054
   Sleeping for 15.0 seconds, 2022-09-21 06:30:19
   Page [[nonsensopedia:pl:Pszczyna]] saved
   Rybna (województwo małopolskie) - WikidataLocation(lat=50.05111111, lon=19.64722222, wikidata='Q7384759')
     SIMC = 0316217
     NTS = 2121618094
   Sleeping for 18.9 seconds, 2022-09-21 06:30:35
   Page [[nonsensopedia:pl:Rybna (województwo małopolskie)]] saved
   
   2 read operations
   Execution time: 38 seconds
   Read operation time: 19.0 seconds
   Script terminated successfully.
   ```

   `$ python geolocbot/bot.py -v --page "Junikowo"`

   ```
   Junikowo - WikidataLocation(lat=52.387405, lon=16.829917, wikidata='Q11729423')
     SIMC = 0969468
     NTS = 4304264011
   Sleeping for 15.7 seconds, 2022-09-21 06:35:49
   Page [[nonsensopedia:pl:Junikowo]] saved
   ```

## Updating TERYT data
To update TERYT datasets, download latest datasets from the
[eTERYT website](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/pobieranie/pliki_pelne.aspx?contrast=default)
and place decompressed files in `geolocbot/teryt_datasets/` directory 
(you can change this path in the `TERYT_DATA_DIR` environment variable). 
Then run the bot. The bot will automatically look for the files with the latest date in the filename.
You can delete old datasets if necessary.

NOTE: Upgrading NTS from 2005 is likely to cause problems with efficient finding 
locality coordinates, as the NTS identifiers in Wikidata are ancient and nobody cares. 
Sorry not sorry.

## License
This project is licensed under the terms of the GNU GPL v3 license.

## Credits
* [Ostrzyciel](https://nonsa.pl/wiki/Użytkownik:Ostrzyciel) 
  for the project idea and great introduction to the topic of programming, 
  that changed my life forever.

## Author
* [Stim](https://nonsa.pl/wiki/Użytkownik:Stim) ([bswck.dev@gmail.com](mailto://bswck.dev@gmail.com) 
  | [GitHub](https://github.com/bswck))