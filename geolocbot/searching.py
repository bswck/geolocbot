# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

"""
Searches:
    *   for pandas.DataFrame TERYT dataframes,
    *   for Wikidata (SPARQL queries builders).

WARNING: Do not import this before importing loaders, otherwise searching classes will work on empty DataFrames.
"""

from scripts.userscripts.geolocbot.geolocbot import *
abc, pandas = libs.abc, libs.pandas


Teryt = object

try:
    resources
except NameError:
    exception = ImportError('please import %r before importing %r' % ('resources', 'filtering'))
    raise exception


class _TerytEntry(Teryt, metaclass=abc.ABCMeta):
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
        self.messages: dict = {
            'args-assigned': 'cannot perform searching: please specify the arguments with their keys in the form '
                             '`key=value`, e.g. search(startswith=\'a\')',
            'unknown-attr': 'couldn\'t fetch TERYT.%s',
            'no-kwargs': 'cannot perform searching: no keyword arguments',
            'no-search-kwargs': 'no keyword arguments for searching (expected minimally 1 from: %s)',
            'empty-field': 'cannot instantiate _TerytEntry search with empty field. Happens mostly due to partially '
                           'intialized `loaders\' module. Please import `loaders\' before importing `filtering\'.',
            'conflicting-kwargs': 'setting more than one keyword argument from %s in one search is impossible',
            'returning-last-frame': {
                'wpk': 'No string in the %s field (column: %r, parsed from: %r) contains substring %r, '
                       'returning last frame no. %s…',
                'npk': 'Could not find value %r in the %s field (column: %r, parsed from: %r), '
                       'returning last frame no. %s…',
                'swn': 'No string in the %s field (column: %r, parsed from: %r) starts with substring %r, '
                       'returning last frame no. %s…'
            },
            'unexpected-kwarg-instance': 'unexpected instance %s of the value of keyword argument %r (expected '
                                         'instance(s): %s).',
            'unexpected-kwarg': f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name '
                                f'in the following list:\n{" " * 11}%s.',
            'results': {
                'found': {
                    'startswith': '[%s] Result(s) for starting with %r:',
                    'endswith': '[%s] Result(s) for ending with %r:',
                    'contains': '[%s] Result(s) for containing %r:',
                    'equal': '[%s] Result(s) for equal to %r:',
                    'no_name_col': '[%s] Result(s) for  name-type key words:'  # TODO
                },
                'not-found': '[%s] Entry frame not found.',
            },
            'parser-failed': 'parser failed: cannot parse more than one TERYT entry (got %s entries)'
        }

        self.simc, self.terc, self.nts = simc, terc, nts
        self.field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self.field_name.lower(), None)
        self.field.search = self.field.loc
        assert self.field is not None, self.messages['unknown-attr'] % self.field_name.lower()
        assert not self.field.empty, self.messages['empty-field']
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.name_col_search_kwargs = ('equal', 'startswith', 'endswith', 'contains')
        self._loc_kw = {'na': False}

        self._id = None  # (!) real value is assigned by parser
        self._index = None  # (!) real value is assigned by parser
        self._voivodship = None  # (!) real value is assigned by parser
        self._powiat = None  # (!) real value is assigned by parser
        self._gmina = None  # (!) real value is assigned by parser
        self._name = None  # (!) real value is assigned by parser
        self._entry_frame = None  # (!) real value is assigned by parser
        self._result = None  # (!) real value is assigned by parser

    @property
    def id(self) -> "str":
        """ Identificator depending on the field type. """
        return self._id

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
    def name(self) -> "str":
        """ Identificator depending on the field type. """
        return self._name

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
        obj = self

        def wrapper(*__args, **__kwargs):
            cls = __args[0]
            item = getattr(cls, '_' + obj.__name__)
            return item if item is not None else NotImplemented
        return wrapper

    # noinspection PyArgumentList
    @id.getter
    @getter
    def id(self): return
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
    @name.getter
    @getter
    def name(self): return
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

        def wrapper(*__args, **__kwargs):
            cls = __args[0]
            setattr(cls, '_' + obj.__name__, None)

        return wrapper

    # noinspection PyArgumentList
    @id.deleter
    @deleter
    def id(self): return
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
    @name.deleter
    @deleter
    def name(self): return
    # noinspection PyArgumentList
    @entry_frame.deleter
    @deleter
    def entry_frame(self): return
    # noinspection PyArgumentList
    @result.deleter
    @deleter
    def result(self): return

    # End of deleters

    @abc.abstractmethod
    def _validate_search_kwargs(self, kwargs) -> "tuple":
        """ Validate kwargs passed to locating function. Check for conflicts, etc. """
        pass

    @abc.abstractmethod
    def search(self, **kwargs) -> "Terc":
        """ Filter the field DataFrame and return self for chaining, e.g. `self.locate(...).voivodship`. """
        pass

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

    @abc.abstractmethod
    def parse(self, dataframe) -> "type(None)":
        """
        Parse the unique data (which is one-row pandas.DataFrame object) and then put it into:
            * self._id,
            * self._voivodship,
            * self._powiat,
            * self._gmina.
        Return: None.
        """
        pass

    def __del__(self):
        del self.id, self.voivodship, self.powiat, self.gmina, self.name, self.entry_frame


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
        self.optional_bool_search_kwargs = ('raise_exception_if_not_found', 'parse', 'matchcase', 'quiet')
        self.search_kwargs = self.name_col_search_kwargs + (
            'voivodship', 'powiat', 'function', 'gmina', 'gmina_type', 'date'
        )
        self.kwargs = self.search_kwargs + self.optional_bool_search_kwargs
        self.conflicts = iter(self.name_col_search_kwargs)

    def _validate_search_kwargs(self, kwargs: dict):
        assert kwargs, self.messages['no-kwargs']

        # Check if arguments occur are expected and if their types are expected
        for kwarg, value in kwargs.items():
            unexpected_kwarg = self.messages['unexpected-kwarg'] % ('search', kwarg, ', '.join(self.search_kwargs))
            is_expected_kwarg = kwarg in self.kwargs
            if not is_expected_kwarg:
                raise TypeError(unexpected_kwarg)
            expected_instance = bool if kwarg in self.optional_bool_search_kwargs else str
            is_expected_instance = isinstance(value, expected_instance)
            unexpected_instance = self.messages['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, expected_instance.__name__
            )
            assert is_expected_instance, unexpected_instance

        assert any([
            kwarg in kwargs for kwarg in self.search_kwargs
        ]), self.messages['no-search-kwargs'] % ', '.join(self.search_kwargs)

        for conflict in self.conflicts:
            more_conflicted_kwargs_assigned = []
            for arg in conflict:
                if arg in kwargs:
                    conflict_explanation = self.messages['conflicting-kwargs'] % ' and '.join([
                        '`%s=…`' % x for x in conflict
                    ])
                    assert not more_conflicted_kwargs_assigned, conflict_explanation
                    more_conflicted_kwargs_assigned.append(arg)

        nmc_str, parse = None, True  # default `parse` value is: True
        modes = self.name_col_search_kwargs + ('no_name_col',)
        m = modes[-1]  # default `m` value is: 'no_name_col'
        for kw in kwargs.copy():
            for md in self.name_col_search_kwargs:
                if kw == md:
                    m = md
                    nmc_str = kwargs[m]
                    del kwargs[md]

        reinf = kwargs.pop('raise_exception_if_not_found', False)
        tools.be_quiet = kwargs.pop('quiet', False)
        parse, matchcase = kwargs.pop('parse', False), kwargs.pop('matchcase', False)

        return m, reinf, parse, matchcase, nmc_str, kwargs

    def search(self, *args, **kwargs):
        """
        Search the TERC database using parameters provided with the Keyword Args.

        Keyword Args – **kwargs:
            equal (str): Search for the entry with *name* strings EQUAL to this string.
            date (str): Date string in format YYYY-[HH-[SS]].
            endswith (str): Search for the entry with *name* strings ENDING with this string.
            function (str): Search for the entry with *function* strings CONTAINING this string.
            gmina (str): Search for the entry with *gmina_type* strings EQUAL this twice 0-filled string.
            gmina_type (str): Search for the entry with *gmina_type* strings EQUAL this once 0-filled
                              string.
            matchcase (bool): Match case of *name* parameter (one defined from `absolute', `partial', `startswith',
                              `endswith') with the searched string. Defaults to False.
            powiat (str): Search for the entry with *powiat* strings CONTAINING this string.
            raise_exception_if_not_found (bool): Raise ValueError if no result was found. Defaults to False.
            startswith (str): Search for the entry with *name* strings STARTING with this string.
            contains (str): Search for the entry with *name* strings CONTAINING this string.
            parse (bool): Sets whether to parse the result and allocate it to properties or not. Defaults to False.
            quiet (bool): Sets output to be quiet if True, does nothing if set to False. Defaults to False.
            voivodship (str): Search for the entry with *voivodship* strings EQUAL to this twice 0-filled
                              string.

        Example:
            >>>
        """
        assert not args, self.messages['args-assigned']
        search_mode, reinf, parse, case, namecol_value, unparsed_cols = self._validate_search_kwargs(kwargs)
        candidate, frames = self.field, [self.field]
        for unparsed_col_name in unparsed_cols:
            _col = self.parse_col[unparsed_col_name]
            # mapping all to strings
            candidate[_col] = candidate[self.parse_col[unparsed_col_name]].map(str)

        namecol = candidate[self.parse_col['name']]

        def failure(): return candidate.empty or candidate.equals(self.field)

        def handle_results():
            nonlocal self
            if failure():
                def handle_failure():
                    self.__del__()
                    if reinf:
                        ve = ValueError(h)
                        raise ve
                    return self
                h = self.messages['results']['not-found'] % self.field_name
                if not reinf:
                    tools.output(h, file='stderr')
                return handle_failure()
            else:
                h = self.messages['results']['found'][search_mode] % (self.field_name, namecol_value)
                tools.output(h, candidate, sep='\n')
                self._entry_frame = candidate
                if parse:
                    self.parse(candidate)
                return self

        if search_mode != 'no_name_col':
            candidate = getattr(self, search_mode)(df=candidate, col=namecol, v=namecol_value, case=case)
            if failure():
                return handle_results()

        for unparsed_col_name, query in unparsed_cols.items():
            containing_col = unparsed_col_name in self.containing_cols
            col = candidate[self.parse_col[unparsed_col_name]]
            stuff = {'df': candidate, 'col': col, 'v': query, 'case': case}
            candidate = self.contains(**stuff) if containing_col else self.equal(**stuff)
            if failure():
                _partial = (self.field_name, self.parse_col[unparsed_col_name], unparsed_col_name, query,
                            len(frames) - 1)
                _startswith = _endswith = _partial
                _absolute = (query, self.field_name, self.parse_col[unparsed_col_name], unparsed_col_name,
                             len(frames) - 1)
                msg = self.messages['returning-last-frame'][search_mode] % eval('_' + search_mode)
                tools.output(msg, file='stderr')
                candidate = frames[-1]
                break

        return handle_results()

    def parse(self, dataframe):
        assert dataframe.size == 1, self.messages['parser-failed'] % dataframe.size
        self._entry_frame = dataframe
        self._name = dataframe.at[0, self.parse_col['name']]


class Simc(_TerytEntry):
    def __init__(self, simc=resources.cached_teryt.simc):
        super(Simc, self).__init__(field_name='simc', simc=simc)

    def _validate_search_kwargs(self, name, **kwargs) -> "tuple":
        pass

    def search(self, **kwargs):
        """
        The SIMC field`s filter.
        WARNING: Keyword arguments sequence INFLUENCES the sequence of filtering!
        """
        pass

    def parse(self, dataframe):
        pass


class Nts(_TerytEntry):
    def __init__(self, nts=resources.cached_teryt.nts):
        super(Nts, self).__init__(field_name='nts', nts=nts)
        self.locdct = {}

    def _validate_search_kwargs(self, name, **kwargs) -> "tuple":
        pass

    def search(self, **kwargs):
        """
        The NTS field`s filter.
        WARNING: Keyword arguments sequence INFLUENCES the sequence of filtering!
        """
        pass

    def parse(self, dataframe):
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
