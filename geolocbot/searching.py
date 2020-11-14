# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

"""
Searches:
    *   for pandas.DataFrame TERYT dataframes,
    *   for Wikidata (SPARQL queries builders).

WARNING: Do not import this before importing loaders, otherwise searching classes will work on empty DataFrames.
"""

from geolocbot.tools import *
abc, better_abc, pandas = geolocbot.libs.abc, geolocbot.libs.better_abc, geolocbot.libs.pandas


Teryt = object

try:
    resources = geolocbot._resources
except NameError:
    raise geolocbot.exceptions.ResourceError('please import %r before importing %r' % ('resources', 'searching'))


class _TerytMetaEntry(metaclass=abc.ABCMeta):
    """ _TerytEntry metaclass """


class TerytSearchingTools(Teryt):
    """ Searching tools for _TerytEntry """


class _TerytEntry(_TerytMetaEntry, metaclass=better_abc.ABCMeta):
    pandas.DataFrame.search = pandas.DataFrame.loc
    """
    Base class holding information about the field of filter and additional geo-info fetched by self.search(...).
    If possible, properties before calling locating via self.search(...) return values suitable for the entire field.
    Otherwise they return ``NotImplemented``.
    """

    def __init__(
            self,
            *,
            field_name: str,
            sub,
            simc_resource=resources.cached_teryt.simc,
            terc_resource=resources.cached_teryt.terc,
            nts_resource=resources.cached_teryt.nts
    ):
        """ Constructor. """
        self._msgs: dict = {
            'args-assigned': 'cannot perform searching: please specify the arguments with their keys in the form '
                             '`key=value`, e.g. search(startswith=\'a\')',
            'unknown-attr': 'couldn\'t fetch TERYT.%s',
            'subclass-is-none': 'field-representative subclass is None',
            'no-kwargs': 'cannot perform searching: no keyword arguments',
            'no-search-kwargs': 'no keyword arguments for searching (expected minimally 1 from: %s)',
            'empty-field': 'cannot instantiate _TerytEntry search with empty field. Happens mostly due to partially '
                           'intialized `loaders\' module. Please import `loaders\' before importing `filtering\'.',
            'conflicting-kwargs': 'setting more than one keyword argument from %s in one search is impossible',
            'returning-last-frame': {
                'contains': 'No string in the %s field (column: %r, parsed from: %r) contains substring %r, '
                            'returning last frame no. %s…',
                'equal': 'Could not find value %r in the %s field (column: %r, parsed from: %r), '
                         'returning last frame no. %s…',
                'startswith': 'No string in the %s field (column: %r, parsed from: %r) starts with substring %r, '
                              'returning last frame no. %s…',
                'endswith': 'No string in the %s field (column: %r, parsed from: %r) starts with substring %r, '
                            'returning last frame no. %s…',
                'no_name_col': 'No string in the %s field (column: %r, parsed from: %r) represents value %r, '
                               'returning last frame no. %s…',
            },
            'unexpected-kwarg-instance': 'unexpected instance %s of the value of keyword argument %r (expected '
                                         'instance(s): %s).',
            'unexpected-kwarg': f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name '
                                f'in the following list:\n{" " * 11}%s.',
            'results': {
                'found': '[%s] Result(s):',
                'not-found': '[%s] Entry frame not found.',
            },
            'parser-failed': 'parser failed: cannot parse more than one TERYT entry (got %s entries)'
        }

        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, self._msgs['unknown-attr'] % self._field_name.lower())
        ensure(not self.field.empty, self._msgs['empty-field'])
        self._sub = sub
        self._name_col_search_kwargs = ('equal', 'startswith', 'endswith', 'contains')
        self.optional_bool_search_kwargs = ('veinf', 'force_parse', 'match_case', 'quiet')
        self.containing_cols = ('date', 'function')
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.conflicts = iter(self._name_col_search_kwargs)
        self.search_kwargs = None
        self.kwargs = None
        self._loc_kw = {'na': False}
        self._perr = geolocbot.exceptions.ParserError
        self.search_mode = None
        self.veinf = None
        self.candidate = None
        self.fparse = None
        self.case = None
        self.namecol_value = None
        self.unparsed_cols = None

        self._id = None  # (!) real value is assigned by parser(s)
        self._integral_id = None  # (!) real value is assigned by parser(s)
        self._region = None  # (!) real value is assigned by parser(s)
        self._subregion = None  # (!) real value is assigned by parser(s)
        self._level = None  # (!) real value is assigned by parser(s)
        self._function = None  # (!) real value is assigned by parser(s)
        self._index = None  # (!) real value is assigned by parser(s)
        self._voivodship = None  # (!) real value is assigned by parser(s)
        self._powiat = None  # (!) real value is assigned by parser(s)
        self._gmina = None  # (!) real value is assigned by parser(s)
        self._gmina_type = None  # (!) real value is assigned by parser(s)
        self._locality_type = None  # (!) real value is assigned by parser(s)
        self._name = None  # (!) real value is assigned by parser(s)
        self._date = None  # (!) real value is assigned by parser(s)
        self._entry_frame = None  # (!) real value is assigned by parser(s)
        self._result = None  # (!) real value is assigned by parser(s)

    @better_abc.abstract_attribute
    def parse_cols(self):
        """
        A dictionary containing:
         *  unparsed names of columns of *field* as keys,
         *  their real representatives (column names of *field*) as values.
        """
        return {}

    @property
    def id(self) -> "str":
        """ Identificator depending on the field type. """
        return self._id

    @property
    def level(self) -> "str":
        """ Level of a locality. """
        return self._level

    @property
    def integral_id(self) -> "str":
        """ Integral ID of a locality. """
        return self._integral_id

    @property
    def region(self) -> "str":
        """ Region. """
        return self._region

    @property
    def subregion(self) -> "str":
        """ Subregion. """
        return self._subregion

    @property
    def function(self) -> "str":
        """ Identificator depending on the field type. """
        return self._function

    @property
    def voivodship(self) -> "str":
        """ Voivodship, for example 'małopolskie'. """
        return self._voivodship

    @property
    def powiat(self) -> "str":
        """ Powiat, for example 'pszczyński' or 'Warszawa' (Warsaw is a city with powiat's rights). """
        return self._powiat

    @property
    def gmina(self) -> "str":
        """ Gmina, for example 'Pszczyna'. """
        return self._gmina

    @property
    def gmina_type(self) -> "str":
        """ Gmina, for example 'Pszczyna'. """
        return self._gmina_type

    @property
    def locality_type(self) -> "str":
        """ Gmina, for example 'Pszczyna'. """
        return self._locality_type

    @property
    def name(self) -> "str":
        """ Value in *name* column. """
        return self._name

    @property
    def date(self) -> "str":
        """ Date of the entry. """
        return self._date

    @property
    def entry_frame(self) -> "pandas.DataFrame":
        """ DataFrame of the entry found by *search()*. """
        return self._entry_frame

    @property
    def result(self) -> "pandas.DataFrame":
        """ DataFrame of the entry found by *search()*. """
        return self._result

    @id.getter
    @getter
    def id(self): return
    @level.getter
    @getter
    def level(self): return
    @integral_id.getter
    @getter
    def integral_id(self): return
    @region.getter
    @getter
    def region(self): return
    @subregion.getter
    @getter
    def subregion(self): return
    @function.getter
    @getter
    def function(self): return
    @voivodship.getter
    @getter
    def voivodship(self): return
    @powiat.getter
    @getter
    def powiat(self): return
    @gmina.getter
    @getter
    def gmina(self): return
    @gmina_type.getter
    @getter
    def gmina_type(self): return
    @locality_type.getter
    @getter
    def locality_type(self): return
    @name.getter
    @getter
    def name(self): return
    @date.getter
    @getter
    def date(self): return
    @entry_frame.getter
    @getter
    def entry_frame(self): return
    @result.getter
    @getter
    def result(self): return
    # End of getters

    # Deleters
    @id.deleter
    @deleter
    def id(self): return
    @level.deleter
    @deleter
    def level(self): return
    @integral_id.deleter
    @deleter
    def integral_id(self): return
    @function.deleter
    @deleter
    def function(self): return
    @region.deleter
    @deleter
    def region(self): return
    @subregion.deleter
    @deleter
    def subregion(self): return
    @voivodship.deleter
    @deleter
    def voivodship(self): return
    @powiat.deleter
    @deleter
    def powiat(self): return
    @gmina.deleter
    @deleter
    def gmina(self): return
    @gmina_type.deleter
    @deleter
    def gmina_type(self): return
    @locality_type.deleter
    @deleter
    def locality_type(self): return
    @name.deleter
    @deleter
    def name(self): return
    @date.deleter
    @deleter
    def date(self): return
    @entry_frame.deleter
    @deleter
    def entry_frame(self): return
    @result.deleter
    @deleter
    def result(self): return

    # End of deleters

    def _validate_search_kwargs(self, kwargs):
        """ Validate kwargs passed to locating function. Check for conflicts, etc. """
        ensure(kwargs, ValueError(self._msgs['no-kwargs']))

        # Check if arguments and their types are expected
        for kwarg, value in kwargs.items():
            unexp_explnt = self._msgs['unexpected-kwarg'] % ('search', kwarg, ', '.join(
                self._sub.kwargs))
            ensure(kwarg in self._sub.kwargs, TypeError(unexp_explnt))
            expected_instance = bool if kwarg in self.optional_bool_search_kwargs else str
            unexpected_instance = self._msgs['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, expected_instance.__name__
            )
            ensure(isinstance(value, expected_instance), TypeError(unexpected_instance))

        ensure(
            any([kwarg in kwargs for kwarg in self._sub.search_kwargs]),
            self._msgs['no-search-kwargs'] % ', '.join(self._sub.search_kwargs)
        )

        for conflict in self.conflicts:
            more_conflicted_kwargs_assigned = []
            for arg in conflict:
                if arg in kwargs:
                    conflict_explanation = self._msgs['conflicting-kwargs'] % ' and '.join([
                        '`%s=…`' % x for x in conflict
                    ])
                    ensure(not more_conflicted_kwargs_assigned, conflict_explanation)
                    more_conflicted_kwargs_assigned.append(arg)

        self.namecol_value, self.fparse = None, True
        modes = self._name_col_search_kwargs + ('no_name_col',)
        self.search_mode = modes[-1]
        for kwarg in kwargs.copy():
            for mode in self._name_col_search_kwargs:
                if kwarg == mode:
                    self.search_mode, self.namecol_value = mode, kwargs[mode]
                    del kwargs[mode]

        self.veinf = kwargs.pop('veinf', False)
        geolocbot.tools.be_quiet = kwargs.pop('quiet', False)
        self.fparse, self.case = kwargs.pop('force_parse', False), kwargs.pop('match_case', False)
        self.unparsed_cols = kwargs
        return True

    @abc.abstractmethod
    def search(self, *args, **kwargs) -> "_TerytEntry":
        """ Search the field DataFrame and return self for chaining, e.g. `self.locate(...).voivodship`. """
        ensure(not args, self._msgs['args-assigned'])
        ensure(self._sub is not None, self._msgs['subclass-is-none'])
        parse_cols = self.parse_cols
        self.search_kwargs = self._name_col_search_kwargs + tuple(parse_cols.keys())
        self.kwargs = self.search_kwargs + self.optional_bool_search_kwargs
        self._validate_search_kwargs(kwargs)

        self.candidate, frames = self.field, [self.field]
        for unparsed_col_name in self.unparsed_cols:
            _col = parse_cols[unparsed_col_name]
            # mapping all to strings
            self.candidate[_col] = self.candidate[parse_cols[unparsed_col_name]].map(str)

        namecol = self.candidate[parse_cols['name']]

        if self.search_mode != 'no_name_col':
            self.candidate = getattr(self, '_' + self.search_mode)(
                df=self.candidate,
                col=namecol,
                value=self.namecol_value,
                case=self.case
            )
            if self._failure():
                return self.results_handler()

        for unparsed_col_name, query in self.unparsed_cols.items():
            containing_col = unparsed_col_name in self.containing_cols
            col = parse_cols[unparsed_col_name]
            stuff = {'df': self.candidate, 'col': col, 'value': query, 'case': self.case}
            self.candidate = self._contains(**stuff) if containing_col else self._equal(**stuff)
            if self._failure():
                fn = getattr(self._field_name)
                _startswith = _endswith = _contains = (fn, parse_cols[unparsed_col_name], unparsed_col_name, query,
                                                       len(frames) - 1)
                _no_name_col = (fn, parse_cols[unparsed_col_name], unparsed_col_name, query,
                                len(frames) - 1)
                _equal = (query, fn, parse_cols[unparsed_col_name], unparsed_col_name,
                          len(frames) - 1)
                msg = self._msgs['returning-last-frame'][self.search_mode] % eval('_' + self.search_mode)
                output(msg, file='stderr')
                self.candidate = frames[-1]
                break

        return self.results_handler()

    @staticmethod
    @colsetter
    def _equal(*, df, col, value, case):
        query = \
            (col == value) \
            if case else \
            (col.str.lower() == value.lower())
        return df.search[query]

    @colsetter
    def _contains(self, *, df, col, value, case):
        query = \
            (col.str.contains(value, case=case, **self._loc_kw))
        return df.search[query]

    @colsetter
    def _startswith(self, *, df, col, value, case):
        query = \
            (col.str.startswith(value, **self._loc_kw)) \
            if case else \
            (col.str.lower().str.startswith(value.lower(), **self._loc_kw))
        return df.search[query]

    @colsetter
    def _endswith(self, *, df, col, value, case):
        query = \
            (col.str.endswith(value, **self._loc_kw)) \
            if case else \
            (col.str.lower().str.endswith(value.lower(), **self._loc_kw))
        return df.search[query]

    def _failure(self): return self.candidate.empty or self.candidate.equals(self.field)

    def results_handler(self):
        if self._failure():
            def failure_handler():
                self.__del__()
                ensure(not self.veinf, ValueError(m))
                return self
            m = self._msgs['results']['not-found'] % self._field_name
            output(m, file='stderr') if not self.veinf else geolocbot.tools.do_nothing()
            return failure_handler()
        else:
            m = self._msgs['results']['found'] % self._field_name
            output(m, self.candidate, sep='\n')
            self._result = self.candidate
            if len(self.candidate) == 1 or self.fparse:
                self.parse()
            return self

    def _fetch_id(self, dataframe=None):
        voivc = self._voivodship
        codes = self._powiat, self._gmina, self._gmina_type
        self._id = ''.join([voivc, *[code for code in codes if code]])

    def parse(self, dataframe=None) -> "type(None)":
        """
        Parser.

        Parse the unique data (which is one-row pandas.DataFrame object) and then put it into: self._id,
        self._voivodship, self._powiat, self._gmina, self._gmina_type, self._name, self._date, self._entry_frame,
        which are accessed by self.id, self.voivodship, self.powiat, self.gmina, self.gmina_type, self.name,
        self.date, self.entry_frame.
        Return: None.
        """
        dataframe, parse_col = dataframe if dataframe is not None else self._sub.result, self.parse_cols

        ensure(len(dataframe) == 1, self._perr(self._msgs['parser-failed'] % len(dataframe)))
        self._entry_frame = dataframe
        nan = geolocbot.libs.numpy.nan

        # Parsing
        [setattr(
            self, '_' + ucn,
            dataframe.iat[0, dataframe.columns.get_loc(pcn)] if dataframe.iat[0, dataframe.columns.get_loc(pcn)]
            is not nan else None
        ) for ucn, pcn in parse_col.items()]

        # Default ID fetching happens in self._fetch_id. However, it is possible to be overriden (as in *Simc* subclass)
        self._fetch_id(dataframe)
        return self._sub

    def __repr__(self): return geolocbot.tools.nice_repr(self._field_name + '_entry', **dict(self))
    def __bool__(self): return not self._failure()

    def __iter__(self):
        for k in self.parse_cols:
            yield k, eval('self.%s' % k)

    def __del__(self):
        for k in self.parse_cols:
            delattr(self, k)


class Terc(_TerytEntry):
    def __init__(self, terc_resource=resources.cached_teryt.terc):
        super(Terc, self).__init__(field_name='terc', sub=self, terc_resource=terc_resource)
        self.parse_cols = {
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ',
            'name': 'NAZWA',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }

    def search(self, *args, **kwargs):
        """
        Search the TERC database using parameters provided with *keyword arguments*.

        Optional keyword arguments:
            equal (str): Search for the entry with *name* strings EQUAL to this string.
            date (str): Date string in format YYYY-[HH-[SS]].
            endswith (str): Search for the entry with *name* strings ENDING with this string.
            function (str): Search for the entry with *function* strings CONTAINING this string.
            gmina (str): Search for the entry with *gmina_type* strings EQUAL to this twice 0-filled string.
            gmina_type (str): Search for the entry with *gmina_type* strings EQUAL to this once 0-filled string.
            match_case (bool): Match case of *name* parameter (one defined from `absolute', `partial', `startswith',
            `endswith') with the searched string. Defaults to False.
            powiat (str): Search for the entry with *powiat* strings CONTAINING this string.
            veinf (bool): Raise ValueError if no result was found. Defaults to False.
            startswith (str): Search for the entry with *name* strings STARTING with this string.
            contains (str): Search for the entry with *name* strings CONTAINING this string.
            force_parse (bool): Sets whether to force the parser to parse the result and allocate it to properties or
            not. Defaults to False.
            quiet (bool): Sets output to be quiet if True, does nothing if set to False. Defaults to False.
            voivodship (str): Search for the entry with *voivodship* strings EQUAL to this twice 0-filled string.

        Examples:
            >>> terc.search(equal='Warszawa', gmina='01', match_case=True, quiet=True).id
            '1465011'

            >>> terc.search(startswith='e')
            [TERC] Result(s):
                 WOJ POW  GMI RODZ     NAZWA                  NAZWA_DOD     STAN_NA
            3321  28  04  nan  NaN  elbląski                     powiat  2020-01-01
            3322  28  04   01    2    Elbląg              gmina wiejska  2020-01-01
            3337  28  05  nan  NaN     ełcki                     powiat  2020-01-01
            3338  28  05   01    1       Ełk              gmina miejska  2020-01-01
            3339  28  05   02    2       Ełk              gmina wiejska  2020-01-01
            3490  28  61  nan  NaN    Elbląg  miasto na prawach powiatu  2020-01-01
            3491  28  61   01    1    Elbląg              gmina miejska  2020-01-01
        """
        return super(Terc, self).search(*args, **kwargs)


class Simc(_TerytEntry):
    def __init__(self, simc_resource=resources.cached_teryt.simc):
        super(Simc, self).__init__(field_name='simc', sub=self, simc_resource=simc_resource)
        self.parse_cols = {
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ_GMI',
            'locality_type': 'RM',
            'name': 'NAZWA',
            'id': 'SYM',
            'integral_id': 'SYMPOD',
            'date': 'STAN_NA',
        }  # (!) MZ column is static (only values == 1), no need to implement it

    def _fetch_id(self, dataframe=None):
        dataframe = dataframe if dataframe is not None else self._sub.result
        self._id = dataframe.iat[0, dataframe.columns.get_loc(self.parse_cols['id'])]
        self._integral_id = dataframe.iat[0, dataframe.columns.get_loc(self.parse_cols['integral_id'])]
        return self

    def search(self, *args, **kwargs): return super(Simc, self).search(*args, **kwargs)


class Nts(_TerytEntry):
    def __init__(self, nts_resource=resources.cached_teryt.nts):
        super(Nts, self).__init__(field_name='nts', sub=self, nts_resource=nts_resource)
        self.parse_cols = {
            'level': 'POZIOM',
            'region': 'REGION',
            'voivodship': 'WOJ',
            'subregion': 'PODREG',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ',
            'name': 'NAZWA',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }

    def search(self, *args, **kwargs): return super(Nts, self).search(*args, **kwargs)


# Modify params for future instanced classes (in variables `simc_filter', `terc_filter', `nts_filter') assigning
# different values to `params' in the following form:
params = {
    'simc': resources.cached_teryt.simc,
    'terc': resources.cached_teryt.terc,
    'nts': resources.cached_teryt.nts
}
simc = Simc(simc_resource=params['simc'])
terc = Terc(terc_resource=params['terc'])
nts = Nts(nts_resource=params['nts'])
