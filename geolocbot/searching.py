# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

"""
Searches:
    *   for pandas.DataFrame TERYT dataframes,
    *   for Wikidata (SPARQL queries builders).

WARNING: Do not import this before importing loaders, otherwise searching classes will work on empty DataFrames.
"""

import geolocbot
from geolocbot.tools import ensure, output
abc, better_abc, pandas = geolocbot.libs.abc, geolocbot.libs.better_abc, geolocbot.libs.pandas


Teryt = object

try:
    resources = geolocbot._resources
except NameError:
    raise geolocbot.exceptions.ResourceError('please import %r before importing %r' % ('resources', 'searching'))


class _TerytMetaEntry(metaclass=abc.ABCMeta):
    """ _TerytEntry metaclass """


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
            simc=resources.cached_teryt.simc,
            terc=resources.cached_teryt.terc,
            nts=resources.cached_teryt.nts
    ):
        """ Constructor. """
        self._messages: dict = {
            'args-assigned': 'cannot perform searching: please specify the arguments with their keys in the form '
                             '`key=value`, e.g. search(startswith=\'a\')',
            'unknown-attr': 'couldn\'t fetch TERYT.%s',
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

        self.simc, self.terc, self.nts = simc, terc, nts
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, self._messages['unknown-attr'] % self._field_name.lower())
        ensure(not self.field.empty, self._messages['empty-field'])
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self._name_col_search_kwargs = ('equal', 'startswith', 'endswith', 'contains')
        self.optional_bool_search_kwargs = ('veinf', 'force_parse', 'match_case', 'quiet')
        self._loc_kw = {'na': False}
        self._ParserError = geolocbot.exceptions.ParserError
        self.search_mode = None
        self.veinf = None
        self.candidate = None
        self.fparse = None
        self.case = None
        self.namecol_value = None
        self.unparsed_cols = None

        self._id = None  # (!) real value is assigned by parsers
        self._function = None  # (!) real value is assigned by parsers
        self._index = None  # (!) real value is assigned by parsers
        self._voivodship = None  # (!) real value is assigned by parsers
        self._powiat = None  # (!) real value is assigned by parsers
        self._gmina = None  # (!) real value is assigned by parsers
        self._gmina_type = None  # (!) real value is assigned by parsers
        self._name = None  # (!) real value is assigned by parsers
        self._date = None  # (!) real value is assigned by parsers
        self._entry_frame = None  # (!) real value is assigned by parsers
        self._result = None  # (!) real value is assigned by parsers

    @better_abc.abstract_attribute
    def parse_col(self):
        """
        A dictionary containing:
         *  unparsed names of columns of *field* as keys,
         *  their real representatives (column names of *field*) as values.
        """
        return {}

    @better_abc.abstract_attribute
    def kwargs(self):
        """
        Tuple with all possible keyword arguments to *search()* method.
        """
        return {}

    @property
    def id(self) -> "str":
        """ Identificator depending on the field type. """
        return self._id

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
    def name(self) -> "str":
        """ Identificator depending on the field type. """
        return self._name

    @property
    def date(self) -> "str":
        """ Identificator depending on the field type. """
        return self._date

    @property
    def entry_frame(self) -> "pandas.DataFrame":
        """ DataFrame of the entry found by the filter. """
        return self._entry_frame

    @property
    def result(self) -> "pandas.DataFrame":
        """ DataFrame of the entry found by the filter. """
        return self._result

    # Getters
    def getter(self):
        """ Decorator for getter methods. In fact, this is a staticmethod. """
        objn, ni = '_' + self.__name__, NotImplemented
        def wrapper(*args, **__kwargs): return getattr(args[0], objn) if getattr(args[0], objn) is not None else ni
        return wrapper

    # noinspection PyArgumentList
    @id.getter
    @getter
    def id(self): return
    # noinspection PyArgumentList
    @function.getter
    @getter
    def function(self): return
    # noinspection PyArgumentList
    @voivodship.getter
    @getter
    def voivodship(self): return
    # noinspection PyArgumentList
    @powiat.getter
    @getter
    def powiat(self): return
    # noinspection PyArgumentList
    @gmina.getter
    @getter
    def gmina(self): return
    # noinspection PyArgumentList
    @gmina_type.getter
    @getter
    def gmina_type(self): return
    # noinspection PyArgumentList
    @name.getter
    @getter
    def name(self): return
    # noinspection PyArgumentList
    @date.getter
    @getter
    def date(self): return
    # noinspection PyArgumentList
    @entry_frame.getter
    @getter
    def entry_frame(self): return
    # noinspection PyArgumentList
    @result.getter
    @getter
    def result(self): return

    # End of getters

    # Deleters
    def deleter(self):
        """ Decorator for deleter methods. In fact, this is a staticmethod. """
        obj = self
        def wrapper(*args, **__kwargs): setattr(args[0], '_' + obj.__name__, None)
        return wrapper

    # noinspection PyArgumentList
    @id.deleter
    @deleter
    def id(self): return
    # noinspection PyArgumentList
    @function.deleter
    @deleter
    def function(self): return
    # noinspection PyArgumentList
    @voivodship.deleter
    @deleter
    @deleter
    def voivodship(self): return
    # noinspection PyArgumentList
    @powiat.deleter
    @deleter
    def powiat(self): return
    # noinspection PyArgumentList
    @gmina.deleter
    @deleter
    def gmina(self): return
    # noinspection PyArgumentList
    @gmina_type.deleter
    @deleter
    def gmina_type(self): return
    # noinspection PyArgumentList
    @name.deleter
    @deleter
    def name(self): return
    # noinspection PyArgumentList
    @date.deleter
    @deleter
    def date(self): return
    # noinspection PyArgumentList
    @entry_frame.deleter
    @deleter
    def entry_frame(self): return
    # noinspection PyArgumentList
    @result.deleter
    @deleter
    def result(self): return

    # End of deleters

    def _validate_search_kwargs(self, field_obj, kwargs) -> "tuple":
        """ Validate kwargs passed to locating function. Check for conflicts, etc. """
        ensure(kwargs, ValueError(self._messages['no-kwargs']))

        # Check if arguments and their types are expected
        for kwarg, value in kwargs.items():
            unexpected_kwarg = self._messages['unexpected-kwarg'] % ('search', kwarg, ', '.join(
                field_obj.kwargs))
            ensure(kwarg in field_obj.kwargs, TypeError(unexpected_kwarg))
            expected_instance = bool if kwarg in field_obj.optional_bool_search_kwargs else str
            is_expected_instance = isinstance(value, expected_instance)
            unexpected_instance = self._messages['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, expected_instance.__name__
            )
            ensure(is_expected_instance, unexpected_instance)

        ensure(
            any([kwarg in kwargs for kwarg in field_obj.search_kwargs]),
            self._messages['no-search-kwargs'] % ', '.join(field_obj.search_kwargs)
        )

        for conflict in field_obj.conflicts:
            more_conflicted_kwargs_assigned = []
            for arg in conflict:
                if arg in kwargs:
                    conflict_explanation = self._messages['conflicting-kwargs'] % ' and '.join([
                        '`%s=…`' % x for x in conflict
                    ])
                    ensure(not more_conflicted_kwargs_assigned, conflict_explanation)
                    more_conflicted_kwargs_assigned.append(arg)

        nmc_str, fparse = None, True
        modes = self._name_col_search_kwargs + ('no_name_col',)
        m = modes[-1]
        for kw in kwargs.copy():
            for md in self._name_col_search_kwargs:
                if kw == md:
                    m = md
                    nmc_str = kwargs[m]
                    del kwargs[md]

        veinf = kwargs.pop('veinf', False)
        geolocbot.tools.be_quiet = kwargs.pop('quiet', False)
        fparse, matchcase = kwargs.pop('force_parse', False), kwargs.pop('match_case', False)

        return m, veinf, fparse, matchcase, nmc_str, kwargs

    @abc.abstractmethod
    def search(self, field_obj, *args, **kwargs) -> "_TerytEntry":
        """ Search the field DataFrame and return self for chaining, e.g. `self.locate(...).voivodship`. """
        ensure(not args, self._messages['args-assigned'])
        trapped_instance = {'field_obj': field_obj}

        field_obj.search_mode, \
            field_obj.veinf, \
            field_obj.fparse, \
            field_obj.case, \
            field_obj.namecol_value, \
            field_obj.unparsed_cols = \
            getattr(field_obj, '_validate_search_kwargs')(field_obj, kwargs)

        field_obj.candidate, frames = field_obj.field, [field_obj.field]
        for unparsed_col_name in field_obj.unparsed_cols:
            _col = field_obj.parse_col[unparsed_col_name]
            # mapping all to strings
            field_obj.candidate[_col] = field_obj.candidate[field_obj.parse_col[unparsed_col_name]].map(str)

        namecol = field_obj.candidate[field_obj.parse_col['name']]

        if field_obj.search_mode != 'no_name_col':
            field_obj.candidate = getattr(field_obj, field_obj.search_mode)(
                df=field_obj.candidate,
                col=namecol,
                v=field_obj.namecol_value,
                case=field_obj.case
            )
            if field_obj.failure(**trapped_instance):
                return field_obj.results_handler(**trapped_instance)

        for unparsed_col_name, query in field_obj.unparsed_cols.items():
            containing_col = unparsed_col_name in field_obj.containing_cols
            col = field_obj.candidate[field_obj.parse_col[unparsed_col_name]]
            stuff = {'df': field_obj.candidate, 'col': col, 'v': query, 'case': field_obj.case}
            field_obj.candidate = field_obj.contains(**stuff) if containing_col else field_obj.equal(**stuff)
            if field_obj.failure(field_obj):
                fn = getattr(field_obj, '_field_name')
                _contains = (fn, field_obj.parse_col[unparsed_col_name], unparsed_col_name, query,
                             len(frames) - 1)
                _startswith = _endswith = _contains
                _no_name_col = (fn, field_obj.parse_col[unparsed_col_name], unparsed_col_name, query,
                                len(frames) - 1)
                _equal = (query, fn, field_obj.parse_col[unparsed_col_name], unparsed_col_name,
                          len(frames) - 1)
                msg = self._messages['returning-last-frame'][field_obj.search_mode] % eval('_' + field_obj.search_mode)
                output(msg, file='stderr')
                field_obj.candidate = frames[-1]
                break

        return field_obj.results_handler(**trapped_instance)

    @staticmethod
    def equal(*, df, col, v, case):
        return df.search[
            (col == v)
            if case else
            (col.str.lower() == v.lower())
        ]

    def contains(self, *, df, col, v, case):
        return df.search[
            (col.str.contains(v, case=case, **self._loc_kw))
        ]

    def startswith(self, *, df, col, v, case):
        return df.search[
            (col.str.startswith(v, **self._loc_kw))
            if case else
            (col.str.lower().str.startswith(v.lower(), **self._loc_kw))
        ]

    def endswith(self, *, df, col, v, case):
        return df.search[
            (col.str.endswith(v, **self._loc_kw))
            if case else
            (col.str.lower().str.endswith(v.lower(), **self._loc_kw))
        ]

    def failure(self, field_obj): return field_obj.candidate.empty or field_obj.candidate.equals(self.field)

    def results_handler(self, *, field_obj):
        inst = {'field_obj': field_obj}  # class instance dict
        if field_obj.failure(**inst):
            def handle_failure():
                self.__del__()
                ensure(not field_obj.veinf, ValueError(m))
                return field_obj
            m = self._messages['results']['not-found'] % self._field_name
            output(m, file='stderr') if not field_obj.veinf else geolocbot.tools.do_nothing()
            return handle_failure()
        else:
            m = self._messages['results']['found'] % self._field_name
            output(m, field_obj.candidate, sep='\n')
            self._result = field_obj.candidate
            if len(field_obj.candidate) == 1 or field_obj.fparse:
                self.parse(**inst)
            return field_obj

    @staticmethod
    def concat_to_id(v, *args): return ''.join([v, *[arg for arg in args if arg]])

    def parse(self, field_obj, id_concatter=concat_to_id, df=None) -> "type(None)":
        """
        Parser.

        Parse the unique data (which is one-row pandas.DataFrame object) and then put it into: self._id,
        self._voivodship, self._powiat, self._gmina, self._gmina_type, self._name, self._date, self._entry_frame,
        which are accessed by self.id, self.voivodship, self.powiat, self.gmina, self.gmina_type, self.name,
        self.date, self.entry_frame.
        Return: None.
        """
        dataframe, parse_col = field_obj.result if not df else df, field_obj.parse_col

        ensure(len(dataframe) == 1, self._ParserError(self._messages['parser-failed'] % len(dataframe)))
        self._entry_frame = dataframe
        nan = geolocbot.libs.numpy.nan

        # Parsing
        [setattr(
            self, '_' + ucn,
            dataframe.iat[0, dataframe.columns.get_loc(pcn)] if dataframe.iat[0, dataframe.columns.get_loc(pcn)]
            is not nan else None
        ) for ucn, pcn in parse_col.items()]

        self._id = id_concatter(self._voivodship, self._powiat, self._gmina, self._gmina_type)

    def __repr__(self): return geolocbot.tools.nice_repr(self._field_name, **dict(self))

    def __iter__(self):
        for k in self.parse_col:
            yield k, eval('self.%s' % k)

    def __del__(self): del self.id, self.voivodship, self.powiat, self.gmina, self.name


class Terc(_TerytEntry):
    def __init__(self, terc=resources.cached_teryt.terc):
        super(Terc, self).__init__(field_name='terc', terc=terc)
        self.parse_col = {
            'name': 'NAZWA',
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }
        self.containing_cols = ('date', 'function')  # filtering with pandas.Series.str.contains(...)
        self.search_kwargs = self._name_col_search_kwargs + tuple(self.parse_col.keys())
        self.kwargs = self.search_kwargs + self.optional_bool_search_kwargs
        self.conflicts = iter(self._name_col_search_kwargs)

    def search(self, *args, **kwargs):
        """
        Search the TERC database using parameters provided with *keyword arguments*.

        Optional keyword arguments:
            equal (str): Search for the entry with *name* strings EQUAL to this string.
            date (str): Date string in format YYYY-[HH-[SS]].
            endswith (str): Search for the entry with *name* strings ENDING with this string.
            function (str): Search for the entry with *function* strings CONTAINING this string.
            gmina (str): Search for the entry with *gmina_type* strings EQUAL this twice 0-filled string.
            gmina_type (str): Search for the entry with *gmina_type* strings EQUAL this once 0-filled string.
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
            >>> terc_search.search(equal='Warszawa', gmina='01', matchcase=True, quiet=True).id
            '1465011'

            >>> terc_search.search(startswith='e')
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
        return super(Terc, self).search(field_obj=self, *args, **kwargs)


class Simc(_TerytEntry):
    def __init__(self, simc=resources.cached_teryt.simc):
        super(Simc, self).__init__(field_name='simc', simc=simc)
        self.parse_col = {
            'id': 'SYM',
            'integral_id': 'SYMPOD',
            'name': 'NAZWA',
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ_GMI',
            'locality_type': 'RM',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }  # (!) MZ column is static (has always value 1), no need to implement it
        self.containing_cols = ('date', 'function')  # filtering with pandas.Series.str.contains(...)
        self.search_kwargs = self._name_col_search_kwargs + tuple(self.parse_col.keys())
        self.kwargs = self.search_kwargs + self.optional_bool_search_kwargs
        self.conflicts = iter(self._name_col_search_kwargs)

    def _validate_search_kwargs(self, name, **kwargs) -> "tuple":
        pass

    def search(self, *args, **kwargs):
        return super(Simc, self).search(field_obj=self, *args, **kwargs)


class Nts(_TerytEntry):
    def __init__(self, nts=resources.cached_teryt.nts):
        super(Nts, self).__init__(field_name='nts', nts=nts)
        self.parse_col = None
        self.kwargs = None

    def _validate_search_kwargs(self, name, **kwargs) -> "tuple":
        pass

    def search(self, **kwargs):
        pass


# Modify params for future instanced classes (in variables `simc_filter', `terc_filter', `nts_filter') assigning
# different values to `params' in the following form:
params = {
    'simc': resources.cached_teryt.simc,
    'terc': resources.cached_teryt.terc,
    'nts': resources.cached_teryt.nts
}
simc_search = Simc(simc=params['simc'])
terc_search = Terc(terc=params['terc'])
nts_search = Nts(nts=params['nts'])
