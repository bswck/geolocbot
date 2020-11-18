# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Searching tool for TERYT register subsystems. """

from geolocbot.tools import *
from geolocbot.libs import *
from geolocbot.auxiliary_types import *


class Teryt(object):
    def __repr__(self): return representation(type(self).__name__, **dict(self))

    def __iter__(self):
        for member_name in [n for n in self.__dict__.keys() if n[:1] != '_']:
            yield member_name, getattr(self, member_name)


resources = geolocbot._resources
_transferred_searches = ()


def get_transferred_searches():
    for transfer in tuple(set(_transferred_searches)):
        yield transfer


class _Tools(Teryt):
    def column_provider(self=Teryt):
        do_nothing(self)  # weak warning: best solution!

        def decorator(meth: typing.Callable):
            def wrapper(*args, **kwargs):
                col, df = kwargs['col'], kwargs['df']
                if isinstance(col, str):
                    ensure(hasattr(df, col), 'no column named %r' % (col,))
                    kwargs['col'] = df[col]
                return meth(*args, **kwargs)
            return wrapper
        return decorator

    column_provider = column_provider()

    @staticmethod
    @column_provider
    @no_type_collisions
    def equal(
            *,
            df: pandas.DataFrame,
            col: (pandas.Series, str),
            value: (str, float),
            case: bool
    ):
        if isinstance(value, float):
            query = \
                (col == value)
        else:
            query = \
                (col == value) \
                if case else \
                (col.str.lower() == value.lower())
        return df.loc[query]

    @staticmethod
    @column_provider
    @no_type_collisions
    def contains(
            *,
            df: pandas.DataFrame,
            col: (pandas.Series, str),
            value: str,
            case: bool
    ):
        query = \
            (col.str.contains(value, case=case, na=False))
        return df.loc[query]

    @staticmethod
    @column_provider
    @no_type_collisions
    def startswith(
            *,
            df: pandas.DataFrame,
            col: (pandas.Series, str),
            value: str,
            case: bool
    ):
        query = \
            (col.str.startswith(value, na=False)) \
            if case else \
            (col.str.lower().str.startswith(value.lower()))
        return df.loc[query]

    @staticmethod
    @column_provider
    @no_type_collisions
    def endswith(
            *,
            df: pandas.DataFrame,
            col: (pandas.Series, str),
            value: str,
            case: bool
    ):
        query = \
            (col.str.endswith(value, na=False)) \
            if case else \
            (col.str.lower().str.endswith(value.lower(), na=False))
        return df.loc[query]

    def __repr__(self): return representation('SearchingTools')


class _FieldSearch(Teryt):
    @no_type_collisions
    def __init__(
            self,
            *,
            dataframe: pandas.DataFrame,
            field_name: str,
            msgs: dict,
            search_mode: str,
            value_spaces: dict,
            case: bool,
            container_values: typing.Iterable,
            startswith_values: typing.Iterable,
            name_space_value: str = '',
    ):
        self.dataframe = dataframe
        self.field_name = field_name
        self.msgs = msgs
        self.search_mode = search_mode
        self.value_spaces = value_spaces
        self.case = case
        self.search_indicators = {}
        self.ineffective_value_space = ''
        self.name_space_value = name_space_value
        self.container_values = container_values
        self.startswith_values = startswith_values

    def failure(self):
        return self.candidate.empty or self.candidate.equals(self.dataframe)

    def shuffle(self):
        keys, values = list(self.search_indicators.keys()), list(self.search_indicators.values())
        inef_keyind = keys.index(self.ineffective_value_space)
        inef_value = values[inef_keyind]
        del keys[inef_keyind], values[inef_keyind]
        keys.insert(inef_keyind + 1, self.ineffective_value_space)
        values.insert(inef_keyind + 1, inef_value)
        self.search_indicators = dict(zip(keys, values))
        return self.search_indicators

    def _search(self, search_indicators):
        self.candidate = self.dataframe.copy()
        self.search_indicators = search_indicators
        value_spaces = self.value_spaces
        self.frames = [self.candidate]

        def initial_search():
            self.candidate = getattr(_Tools, self.search_mode)(
                df=self.candidate,
                col=value_spaces['name'],
                value=self.name_space_value,
                case=self.case
            )

            self.frames.append(self.candidate)

        if self.search_mode != 'no_name_col':
            initial_search()
            if self.failure():
                return pandas.DataFrame()

        attempts = 0
        max_attempts = len(self.search_indicators)
        done = False

        def search_loop():
            nonlocal attempts, done
            for value_space, query in self.search_indicators.items():
                attempts += 1
                if value_space in self.value_spaces:
                    col = self.value_spaces[value_space]
                else:
                    continue
                stuff = dict(df=self.candidate, col=col, value=query, case=self.case)
                self.candidate = \
                    _Tools.contains(**stuff) if value_space in self.container_values else \
                    _Tools.startswith(**stuff) if value_space in self.startswith_values else \
                    _Tools.equal(**stuff)

                if self.failure():
                    self.candidate = self.frames[-1]
                    if attempts <= max_attempts:
                        self.ineffective_value_space = value_space
                        self.shuffle()
                        search_loop()
                    else:
                        done = True
                        break

                self.frames.append(self.candidate)

        search_loop() if not done else do_nothing()
        return self.candidate

    @no_type_collisions
    def __call__(
            self,
            search_indicators: dict
    ):
        """ Wrapper for self._search(). """
        return self._search(search_indicators=search_indicators)


class TerytField(abstract_class, metaclass=better_abstract_metaclass):
    translation_table = None

    def __init__(
            self,
            *,
            field_name: str,
            sub,
            simc_resource=resources.cached_teryt.simc,
            terc_resource=resources.cached_teryt.terc,
            nts_resource=resources.cached_teryt.nts
    ):
        geolocbot.tools.tf = self
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
                'contains': 'No value in the %(fn)s field (column: %(pc)r, parsed from: %(uc)r) contains substring '
                            '%(q)r, returning last frame no. %(lf)s…',
                'equal': 'Could not find value %(q)r in the %(fn)s field (column: %(pc)r, parsed from: %(uc)r), '
                         'returning last frame no. %(lf)s…',
                'startswith': 'No value in the %(fn)s field (column: %(pc)r, parsed from: %(uc)r) starts with '
                              'substring %(q)r, returning last frame no. %(lf)s…',
                'endswith': 'No value in the %(fn)s field (column: %(pc)r, parsed from: %(uc)r) starts with substring '
                            '%r, returning last frame no. %(lf)s…',
                'no_name_col': 'No value in the %(fn)s field (column: %(pc)r, parsed from: %(uc)r) represents value '
                               '%(q)r, returning last frame no. %(lf)s…',
            },
            'unexpected-kwarg-instance': 'unexpected instance %s of the value of keyword argument %r (expected '
                                         'instance(s): %s).',
            'unexpected-kwarg': f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name '
                                f'in the following list:\n{" " * 11}%s.',
            'results': {
                'found': '[%s] Result(s):',
                'not-found': '[%s] Entry frame not found.',
            },
            'parser-failed': 'parser failed: cannot parse more than one TERYT entry (got %s entries)',
            'not-teryt-subclass': 'cannot transfer search indicators not to TerytField subclass',
            'not-parsed-for-indicators': 'cannot perform getting indicators from properties if search results were not '
                                         'parsed (no parsed properties)',
            'no-sfo': 'cannot evaluate subclass field object with provided name %r'
        }

        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, self._msgs['unknown-attr'] % self._field_name.lower())
        ensure(not self.field.empty, self._msgs['empty-field'])
        self._sfo: TerytField = sub  # subclass field object
        self._gi_sfo = None  # subclass field object for indicators getting from properties
        self._candidate = None
        self._container_values = ('function',)
        self._nametype_values = ('equal', 'startswith', 'endswith', 'contains')
        self._optbool_values = ('veinf', 'force_parse', 'parse', 'by_codes', 'match_case', 'quiet')
        self._perr = geolocbot.exceptions.ParserError
        self._startswith_values = ('date',)
        self.case = None
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.conflicts = (self._nametype_values, ('force_parse', 'parse'))
        self.fparse, self.kwargs, self.name_space_value, self.parse = None, None, None, None
        self.search_indicators, self.search_kwargs, self.search_mode, self.veinf = None, None, None, None
        self.parsed = False
        self._to_get_id = {}
        self._rest = {}

        # Single entry values
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
        self._results = None  # (!) real value is assigned by parser(s)
        # End of single entry values

    def __repr__(self): return representation(self._field_name + '_field' if not self.parsed
                                              else self._field_name + '_field_and_entry',
                                              **dict(self))

    def __iter__(self):
        for k in self.value_spaces:
            if eval('self.%s' % k):
                yield k, eval('self.%s' % k)

    def __del__(self):
        for k in self.value_spaces:
            delattr(self, k)

    @abstractattribute
    def value_spaces(self): return {}

    @abstractattribute
    def translatable_values(self): return {}

    @property
    @getter_itself
    def level(self): return
    @level.deleter
    @deleter
    def level(self): return

    @property
    @getter_itself
    def region(self): return
    @region.deleter
    @deleter
    def region(self): return

    @property
    @getter_itself
    def subregion(self): return
    @subregion.deleter
    @deleter
    def subregion(self): return

    @property
    @getter_itself
    def voivodship(self): return
    @voivodship.deleter
    @deleter
    def voivodship(self): return

    @property
    @getter_itself
    def powiat(self): return
    @powiat.deleter
    @deleter
    def powiat(self): return

    @property
    @getter_itself
    def gmina(self): return
    @gmina.deleter
    @deleter
    def gmina(self): return

    @property
    @getter_itself
    def gmina_type(self): return
    @gmina_type.deleter
    @deleter
    def gmina_type(self): return

    @property
    @getter_itself
    def locality_type(self): return
    @locality_type.deleter
    @deleter
    def locality_type(self): return

    @property
    @getter_itself
    def name(self): return
    @name.deleter
    @deleter
    def name(self): return

    @property
    @getter_itself
    def function(self): return
    @function.deleter
    @deleter
    def function(self): return

    @property
    @getter_itself
    def id(self): return
    @id.deleter
    @deleter
    def id(self): return

    @property
    @getter_itself
    def integral_id(self): return
    @integral_id.deleter
    @deleter
    def integral_id(self): return

    @property
    @getter_itself
    def date(self): return
    @date.deleter
    @deleter
    def date(self): return

    @property
    @getter_itself
    def entry_frame(self): return
    @entry_frame.deleter
    @deleter
    def entry_frame(self): return

    @property
    @getter_itself
    def results(self): return
    @results.deleter
    @deleter
    def results(self): return

    def _search_hook(self, _args, _kwargs):
        ensure(not _args, self._msgs['args-assigned'])
        ensure(_kwargs, ValueError(self._msgs['no-kwargs']))
        self.search_kwargs = self._nametype_values + tuple(self.value_spaces.keys())
        self.kwargs = self.search_kwargs + self._optbool_values

        # 1. Check if arguments and their types are expected
        for kwarg, value in _kwargs.items():
            ensure(
                kwarg in self.kwargs, TypeError(self._msgs['unexpected-kwarg'] % ('search', kwarg, ', '.join(
                    self.kwargs)))
            )
            expected_instance = bool if kwarg in self._optbool_values else (str, float, IdTranslation)
            unexpected_instance = self._msgs['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, ', '.join(
                            ['%r' % obj_type.__name__ for obj_type in expected_instance]
                        ) if isinstance(expected_instance, typing.Iterable) else type(expected_instance).__name__
            )
            if isinstance(value, IdTranslation):
                _kwargs[kwarg] = str(value)
            ensure(isinstance(value, expected_instance), TypeError(unexpected_instance))

        # 2. Check if any search keyword arg has been provided
        ensure(
            any([kwarg in _kwargs for kwarg in self.search_kwargs]),
            self._msgs['no-search-kwargs'] % ', '.join(self.search_kwargs)
        )

        # 3. Handle conflicts
        for conflicted in self.conflicts:
            conflict = []
            for arg in conflicted:
                if arg in _kwargs:
                    formatter = ' and '.join(['\'%s=…\'' % x for x in conflicted])
                    ensure(not conflict, self._msgs['conflicting-kwargs'] % formatter)
                    conflict.append(arg)

        self.name_space_value, self.fparse = None, True
        modes = self._nametype_values + ('no_name_col',)
        self.search_mode = modes[-1]

        # 4. Get the search mode and name-type value
        for kwarg in _kwargs.copy():
            for mode in self._nametype_values:
                if kwarg == mode:
                    self.search_mode, self.name_space_value = mode, _kwargs[mode]
                    del _kwargs[mode]

        # 5. Pop the boolean options
        self.veinf = _kwargs.pop('veinf', False)
        if _kwargs.pop('quiet', False):
            geolocbot.tools.be_quiet = True
        self.parse = _kwargs.pop('parse', True)
        self.fparse, self.case = _kwargs.pop('force_parse', False), _kwargs.pop('match_case', False)
        self.by_codes = _kwargs.pop('by_codes', False)

        # 6. Set the search indicators
        if not self.by_codes:
            _kwargs = self._get_IDs(**_kwargs)
        self.search_indicators = _kwargs
        return True

    # @reraise(geolocbot.exceptions.SearchError)  ← TODO
    @tfhook(_search_hook)
    def search(self, *_args, **_kwargs) -> "TerytField":
        value_spaces = self.value_spaces
        self._candidate, frames = self.field, [self.field]
        for value_space in self.search_indicators:
            _col = value_spaces[value_space]
            self.field[_col] = self.field[value_spaces[value_space]].map(str)  # mapping all to strings
        self._candidate = _FieldSearch(
            dataframe=self.field,
            field_name=self._field_name,
            msgs=self._msgs,
            search_mode=self.search_mode,
            value_spaces=self.value_spaces,
            case=self.case,
            name_space_value=self.name_space_value,
            container_values=self._container_values,
            startswith_values=self._startswith_values
        )(search_indicators=self.search_indicators)

        return self._results_handler()

    @abstractmethod
    def fetch_id(self) -> "TerytField":
        pass

    def _gi_hook(self, _args, _kwargs):
        sfo_n = _args[0]
        ensure(all([sfo_n, not sfo_n.isspace(), globals().get(sfo_n) is not None]), self._msgs['no-sfo'] % sfo_n)
        self._gi_sfo = eval(sfo_n)
        ensure(
            issubclass(type(self._gi_sfo), TerytField), self._msgs['not-teryt-subclass']
        )
        ensure(self.parsed, self._msgs['not-parsed-for-indicators'])

    @tfhook(_gi_hook)
    @no_type_collisions
    def get_indicators(self, _sfo_name: str):
        sfo = self._gi_sfo
        properties = dict(self)
        name_space_value = properties.pop('name')
        prop_copy = properties.copy()
        [
            properties.__setitem__(k, str(v))
            if k in sfo.value_spaces and str(v)
            else properties.__delitem__(k)
            for k, v in prop_copy.items()
        ]
        kwds = {
            'by_codes': True,
            'equal': name_space_value,
            'veinf': self.veinf,
            'force_parse': self.fparse,
            'match_case': self.case,
        }
        yield dict(**properties, **kwds)
        yield sfo

    @no_type_collisions
    def transfer(self, sfo_name: str) -> "TerytField":
        stuff, sfo = self.get_indicators(sfo_name)
        global _transferred_searches
        _transferred_searches = _transferred_searches + (self, sfo.search(**stuff))
        return _transferred_searches[-1]

    @no_type_collisions
    def _gids_hook(self, _args, _kwargs):
        ek, err = tuple(self.value_spaces.keys()), TypeError
        # 1. Check if all keyword args are expected
        [ensure(kwarg in ek, err(self._msgs['unexpected-kwarg'] % ('code', kwarg, ', '.join(ek)))) for kwarg in _kwargs]
        # 2. Parse
        for kwn, kwv in _kwargs.items():
            if hasattr(IdTable, kwn + 's'):
                self._to_get_id.update({kwn: kwv})
            self._rest.update({kwn: kwv})

    @tfhook(_gids_hook)
    def _get_IDs(self, **_kwargs):
        id_indicators = {**self._rest}
        spaces = list(self.value_spaces.keys())
        for value_space, value in self._to_get_id.items():
            id_dataframe = getattr(IdTable, value_space + 's')
            entry = _FieldSearch(
                dataframe=id_dataframe,
                field_name=getattr(self.translation_table, '_field_name'),
                msgs=self._msgs,
                search_mode='equal',
                value_spaces=self.value_spaces,
                case=False,
                container_values=self._container_values,
                startswith_values=self._startswith_values,
                name_space_value=value
            )(search_indicators=id_indicators)
            id_snippet = entry.iat[0, entry.columns.get_loc(self.value_spaces[value_space])]
            id_indicators.update({value_space: id_snippet})
            if value_space != spaces[0]:
                quantum = spaces.index(value_space) - 1
                for rot in range(quantum + 1):
                    prev_ = spaces[quantum - rot]
                    id_indicators[prev_] = entry.iat[0, entry.columns.get_loc(self.value_spaces[prev_])]
        return id_indicators

    def _translate_hook(self, _args, _kwargs):
        value_space = _args[0]
        # value = _args[1]
        ensure(
            value_space in self.translatable_values,
            'untranslatable value space %r' % value_space
        )

    @tfhook(_translate_hook)
    @no_type_collisions
    def translate(self, value_space: str, value: str):
        value = str(value)
        translation_table = self.translation_table
        indicators = {}
        spaces = list(self.value_spaces.keys())

        if value_space != spaces[0]:
            quantum = spaces.index(value_space) - 1
            for rot in range(quantum + 1):
                prev_ = spaces[quantum - rot]
                indicators[prev_] = str(getattr(self, '_' + prev_))
        
        indicators[value_space] = value
        
        if value_space != list(self.value_spaces.keys())[-1]:
            next_ = list(self.value_spaces.keys())[list(self.value_spaces.keys()).index(value_space) + 1]
            indicators[next_] = 'nan'

        translation_dataframe = _FieldSearch(
            dataframe=translation_table.field,
            field_name=getattr(translation_table, '_field_name'),
            msgs=getattr(translation_table, '_msgs'),
            search_mode='no_name_col',
            value_spaces=translation_table.value_spaces,
            case=self.case,
            container_values=getattr(translation_table, '_container_values'),
            startswith_values=getattr(translation_table, '_startswith_values'),
        )(search_indicators=indicators)

        translation = translation_dataframe.iat[
            0, translation_dataframe.columns.get_loc(translation_table.value_spaces['name'])
        ]

        return translation
    
    def failure(self):
        return self._candidate.empty or self._candidate.equals(self.field)

    @no_type_collisions
    def parse_single_entry(self, dataframe: pandas.DataFrame = None) -> "type(None)":
        dataframe, value_spaces = dataframe if dataframe is not None else self.results, self.value_spaces

        ensure(len(dataframe) == 1, self._perr(self._msgs['parser-failed'] % len(dataframe)))
        self._entry_frame = dataframe

        for value_space, real_value in value_spaces.items():
            value = dataframe.iat[0, dataframe.columns.get_loc(real_value)]
            value = None if value == 'nan' or value is nan else value
            if value is not None:
                setattr(
                    self, '_' + value_space,
                    IdTranslation(ID=value, translation=self.translate(value_space, value))
                    if value_space in self.translatable_values
                    else value
                )

        self.fetch_id()
        self.parsed = True
        return self._sfo

    def _results_handler(self):
        if self.failure():
            def _failure_handler():
                self.__del__()
                ensure(not self.veinf, ValueError(self._msgs['results']['not-found'] % self._field_name))
                return self._sfo
            output(self._msgs['results']['not-found'] % self._field_name, file='stderr') \
                if not self.veinf else geolocbot.tools.do_nothing()
            return _failure_handler()
        else:
            output(self._msgs['results']['found'] % self._field_name, self._candidate, sep='\n')
            self._results = self._candidate
            if (len(self._candidate) == 1 or self.fparse) and self.parse:
                self.parse_single_entry()
            return self._sfo


class Terc(TerytField):
    def __init__(self, terc_resource=resources.cached_teryt.terc):
        super(Terc, self).__init__(field_name='terc', sub=self, terc_resource=terc_resource)
        self.value_spaces = {
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ',
            'name': 'NAZWA',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }
        self.translatable_values = \
            (
                'voivodship',
                'powiat',
                'gmina',
                'gmina_type',
            )
        TerytField.translation_table = self

    def fetch_id(self):
        self._id = str('voivodship') + str('powiat') + str('gmina') + str('gmina_type')
        return self


class Simc(TerytField):
    def __init__(self, simc_resource=resources.cached_teryt.simc):
        super(Simc, self).__init__(field_name='simc', sub=self, simc_resource=simc_resource)
        self.value_spaces = {
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
        self.translatable_values = \
            (
                'voivodship',
                'powiat',
                'gmina',
                'gmina_type'
            )

    def fetch_id(self, dataframe=None):
        dataframe = dataframe if dataframe is not None else self.results
        self._id = dataframe.iat[0, dataframe.columns.get_loc(self.value_spaces['id'])]
        self._integral_id = dataframe.iat[0, dataframe.columns.get_loc(self.value_spaces['integral_id'])]
        return self


class Nts(TerytField):
    def __init__(self, nts_resource=resources.cached_teryt.nts):
        super(Nts, self).__init__(field_name='nts', sub=self, nts_resource=nts_resource)
        self.value_spaces = {
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
        self.translatable_values = \
            (
                'level',
                'region',
                'voivodship',
                'subregion',
                'powiat',
                'gmina',
                'gmina_type',
            )

    def fetch_id(self, dataframe=None):
        self._id = str(self._level) + \
                   str(self._region) + \
                   str(self._subregion) + \
                   str(self._voivodship) + \
                   str(self._powiat) + \
                   str(self._gmina) + \
                   str(self._gmina_type)
        return self


# You can modify params for future instanced classes (in variables *simc_filter*, *terc_filter*, *nts_filter*) assigning
# custom values in the following form:
params = {
    'simc': resources.cached_teryt.simc,
    'terc': resources.cached_teryt.terc,
    'nts': resources.cached_teryt.nts
}
simc = Simc(simc_resource=params['simc'])
terc = Terc(terc_resource=params['terc'])
nts = Nts(nts_resource=params['nts'])


# (!) never ever instantiate _IdTable in →this← file
class _IdTable(Teryt):
    def __init__(self):
        self._search = TerytField.translation_table.search
        self.regions = nts.search(function='region', by_codes=True, quiet=True).results
        self.subregions = nts.search(function='podregion', by_codes=True, quiet=True).results
        self.voivodships = self._search(function='województwo', by_codes=True, quiet=True).results
        self.powiats = self._search(function='powiat', by_codes=True, quiet=True).results
        self.gminas = self._search(function='gmina', by_codes=True, quiet=True).results


IdTable = Teryt  # (!) real value is: _IdTable()
