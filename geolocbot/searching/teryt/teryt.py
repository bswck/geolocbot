# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

"""
Searching tool for TERYT register subsystems.

WARNING: Do not import this before importing loaders, otherwise searching classes will attempt to work on empty
DataFrames.
"""

from geolocbot.tools import *
from geolocbot.libs import *
import geolocbot


TranslationDict = geolocbot.auxiliary_types.TranslatableValue
Teryt = object

try:
    resources = geolocbot._resources
except NameError:
    raise geolocbot.exceptions.ResourceError('please import %r before importing %r' % ('resources', 'searching'))


class _SearchingTools(Teryt):
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


class _TerytFieldSearch(Teryt):
    @no_type_collisions
    def __init__(
            self,
            *,
            dataframe: pandas.DataFrame,
            field_name: str,
            msgs: dict,
            search_mode: str,
            value_spaces: dict,
            errors: str = 'handle',
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
        self.errors = errors
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

    def _real_search(self, search_indicators):
        self.candidate = self.dataframe.copy()
        self.search_indicators = search_indicators
        value_spaces = self.value_spaces
        self.frames = [self.candidate]

        def initial_search():
            self.candidate = getattr(_SearchingTools, self.search_mode)(
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
                    _SearchingTools.contains(**stuff) if value_space in self.container_values else \
                    _SearchingTools.startswith(**stuff) if value_space in self.startswith_values else \
                    _SearchingTools.equal(**stuff)

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

        if not done:
            search_loop()

        return self.candidate

    @no_type_collisions
    def __call__(
            self,
            search_indicators: dict
    ):
        return self._real_search(search_indicators=search_indicators)


class TerytField(abstract_class, metaclass=better_abstract_metaclass):
    translate_table = None

    def __init__(
            self,
            *,
            field_name: str,
            sub,
            simc_resource=resources.cached_teryt.simc,
            terc_resource=resources.cached_teryt.terc,
            nts_resource=resources.cached_teryt.nts
    ):
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
            'parser-failed': 'parser failed: cannot parse more than one TERYT entry (got %s entries)'
        }

        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, self._msgs['unknown-attr'] % self._field_name.lower())
        ensure(not self.field.empty, self._msgs['empty-field'])
        self._sfo: TerytField = sub  # subclass field object
        self._candidate = None
        self._container_values = ('function',)
        self._nametype_values = ('equal', 'startswith', 'endswith', 'contains')
        self._optbool_values = ('veinf', 'force_parse', 'parse', 'match_case', 'quiet')
        self._perr = geolocbot.exceptions.ParserError
        self._startswith_values = ('date',)
        self.case = None
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.conflicts = (self._nametype_values, ('force_parse', 'parse'))
        self.fparse = None
        self.kwargs = None
        self.name_space_value = None
        self.parse = None
        self.search_indicators = None
        self.search_kwargs = None
        self.search_mode = None
        self.veinf = None

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

    @abstractattribute
    def value_spaces(self): return {}

    @abstractattribute
    def translatable_values(self): return {}

    @property
    def id(self) -> "str": return self._id

    @id.getter
    @getter
    def id(self):
        return

    @id.deleter
    @deleter
    def id(self):
        return

    @property
    def level(self) -> "str": return self._level

    @level.getter
    @getter
    def level(self):
        return

    @level.deleter
    @deleter
    def level(self): return

    @property
    def integral_id(self) -> "str": return self._integral_id
    @property
    def region(self) -> "str": return self._region
    @property
    def subregion(self) -> "str": return self._subregion
    @property
    def function(self) -> "str": return self._function
    @property
    def voivodship(self) -> "str": return self._voivodship
    @property
    def powiat(self) -> "str": return self._powiat
    @property
    def gmina(self) -> "str": return self._gmina
    @property
    def gmina_type(self) -> "str": return self._gmina_type
    @property
    def locality_type(self) -> "str": return self._locality_type
    @property
    def name(self) -> "str": return self._name
    @property
    def date(self) -> "str": return self._date
    @property
    def entry_frame(self) -> "pandas.DataFrame": return self._entry_frame
    @property
    def results(self) -> "pandas.DataFrame": return self._results

    # Getters
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
    @results.getter
    @getter
    def results(self): return pandas.DataFrame()
    # End of getters

    # Deleters
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
    @results.deleter
    @deleter
    def results(self): return
    # End of deleters

    def failure(self): return self._candidate.empty or self._candidate.equals(self.field)

    @no_type_collisions
    def _validate(self, kwargs: dict):
        ensure(not not kwargs, ValueError(self._msgs['no-kwargs']))

        # Check if arguments and their types are expected
        for kwarg, value in kwargs.items():
            ensure(
                kwarg in self.kwargs, TypeError(self._msgs['unexpected-kwarg'] % ('search', kwarg, ', '.join(
                    self.kwargs)))
            )
            expected_instance = bool if kwarg in self._optbool_values else (str, float, TranslatableValue)
            unexpected_instance = self._msgs['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, ', '.join(
                            ['%r' % obj_type.__name__ for obj_type in expected_instance]
                        ) if isinstance(expected_instance, typing.Iterable) else type(expected_instance).__name__
            )
            if isinstance(value, TranslatableValue):
                kwargs[kwarg] = str(value)
            ensure(isinstance(value, expected_instance), TypeError(unexpected_instance))

        ensure(
            any([kwarg in kwargs for kwarg in self.search_kwargs]),
            self._msgs['no-search-kwargs'] % ', '.join(self.search_kwargs)
        )

        for conflict in self.conflicts:
            conflicted = []
            for arg in conflict:
                if arg in kwargs:
                    formatter = ' and '.join(['\'%s=…\'' % x for x in conflict])
                    ensure(not conflicted, self._msgs['conflicting-kwargs'] % formatter)
                    conflicted.append(arg)

        self.name_space_value, self.fparse = None, True
        modes = self._nametype_values + ('no_name_col',)
        self.search_mode = modes[-1]
        for kwarg in kwargs.copy():
            for mode in self._nametype_values:
                if kwarg == mode:
                    self.search_mode, self.name_space_value = mode, kwargs[mode]
                    del kwargs[mode]

        self.veinf = kwargs.pop('veinf', False)
        if kwargs.pop('quiet', False):
            geolocbot.tools.be_quiet = True
        self.parse = kwargs.pop('parse', True)
        self.fparse, self.case = kwargs.pop('force_parse', False), kwargs.pop('match_case', False)
        self.search_indicators = kwargs
        return True

    def search(self, *args, **kwargs) -> "TerytField":
        ensure(not args, self._msgs['args-assigned'])
        ensure(self._sfo is not None, self._msgs['subclass-is-none'])
        value_spaces = self.value_spaces
        self.search_kwargs = self._nametype_values + tuple(value_spaces.keys())
        self.kwargs = self.search_kwargs + self._optbool_values
        self._validate(kwargs)
        self._candidate, frames = self.field, [self.field]
        for value_space in self.search_indicators:
            _col = value_spaces[value_space]
            self.field[_col] = self.field[value_spaces[value_space]].map(str)  # mapping all to strings
        self._candidate = _TerytFieldSearch(
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

    @abstractmethod
    def fetch_id(self) -> "TerytField":
        pass

    def properties_to_indicators(self, field_object_name: str):
        field_object = eval(field_object_name)
        ensure(
            issubclass(type(field_object), TerytField), 'cannot transfer search indicators not to TerytField subclass'
        )
        properties = dict(self)
        name_space_value = properties.pop('name').raw
        prop_copy = properties.copy()
        [
            properties.__setitem__(k, dict(v)['raw'])
            if k in field_object.value_spaces and dict(v)['raw']
            else properties.__delitem__(k)
            for k, v in prop_copy.items()
        ]
        kwds = {
            self.search_mode: name_space_value,
            'veinf': self.veinf,
            'force_parse': self.fparse,
            'match_case': self.case,
        }
        return dict(
            zip(
                list(properties.keys()) + list(kwds.keys()),
                list(properties.values()) + list(kwds.values())
            )
        ), field_object

    @no_type_collisions
    def transfer(self, field_object_name: str) -> "TerytField":
        stuff, field_object = self.properties_to_indicators(field_object_name=field_object_name)
        return field_object.search(**stuff)

    @no_type_collisions
    def translate(self, value_space: str, value: str):
        ensure(
            value_space in self.translatable_values['locally'] or value_space in self.translatable_values['globally'],
            'untranslatable value space %r' % value_space
        )
        value = str(value)
        trans_mode = 'locally' if value_space in self.translatable_values['locally'] else 'globally'
        indicators = {}
        spaces = list(self.value_spaces.keys())

        if value_space != spaces[0]:
            quantum = spaces.index(value_space) - 1
            for q in range(quantum + 1):
                prev_value_space = spaces[quantum - q]
                indicators[prev_value_space] = str(getattr(self, '_' + prev_value_space))
        indicators[value_space] = value
        if value_space != list(self.value_spaces.keys())[-1]:
            next_value_space = list(self.value_spaces.keys())[list(self.value_spaces.keys()).index(value_space) + 1]
            indicators[next_value_space] = 'nan'

        translate_table = self.translate_table if trans_mode == 'globally' else self

        translation_dataframe = _TerytFieldSearch(
            dataframe=translate_table.field,
            field_name=getattr(translate_table, '_field_name'),
            msgs=getattr(translate_table, '_msgs'),
            search_mode='no_name_col',
            value_spaces=translate_table.value_spaces,
            errors='ignore',
            case=self.case,
            container_values=getattr(translate_table, '_container_values'),
            startswith_values=getattr(translate_table, '_startswith_values'),
        )(search_indicators=indicators)

        translation = translation_dataframe.iat[
            0, translation_dataframe.columns.get_loc(translate_table.value_spaces['name'])
        ]

        return translation

    @no_type_collisions
    def parse_single_entry(self, dataframe: pandas.DataFrame = None) -> "type(None)":
        dataframe, value_spaces = dataframe if dataframe is not None else self.results, self.value_spaces

        ensure(len(dataframe) == 1, self._perr(self._msgs['parser-failed'] % len(dataframe)))
        self._entry_frame = dataframe

        # Parsing
        for value_space, real_value in value_spaces.items():
            value = dataframe.iat[0, dataframe.columns.get_loc(real_value)]
            value = None if value == 'nan' or value is nan else value
            if value is not None:
                setattr(
                    self, '_' + value_space,
                    TranslatableValue(raw=value, translation=self.translate(value_space, value))
                    if value_space in self.translatable_values['globally']
                    or value_space in self.translatable_values['locally']
                    else TranslatableValue(raw=value)
                )

        self.fetch_id()
        return self._sfo

    def __repr__(self): return geolocbot.tools.representation(self._field_name + '_entry', **dict(self))

    def __iter__(self):
        for k in self.value_spaces:
            if eval('self.%s' % k) is not NotImplemented:
                yield k, eval('self.%s' % k)

    def __del__(self):
        for k in self.value_spaces:
            delattr(self, k)


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
            {
                'globally':
                    (
                        'voivodship',
                        'powiat',
                        'gmina',
                        'gmina_type',
                    ),
                'locally':
                    ()
            }

    def getstr(self, attrname):
        str_ = getattr(self, attrname, TranslatableValue()).raw
        return str_ if str_ is not NotImplemented or str_ is not None else ''

    def fetch_id(self):
        self._id = self.getstr('voivodship') + self.getstr('powiat') + self.getstr('gmina') + self.getstr('gmina_type')
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
            {
                'globally':
                    (
                        'voivodship',
                        'powiat',
                        'gmina',
                        'gmina_type',
                    ),
                'locally':
                    ()
            }

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
            {
                'globally':
                    (
                        'level',
                        'region',
                        'voivodship',
                        'subregion',
                        'powiat',
                        'gmina',
                        'gmina_type',
                    ),
                'locally':
                    ()
            }

    def fetch_id(self, dataframe=None):
        self._id = self._region + self._subregion + self._voivodship + self._powiat + self._gmina + self._gmina_type
        return self


# Modify params for future instanced classes (in variables `simc_filter', `terc_filter', `nts_filter') assigning
# different values to `params' in the following form:
params = {
    'simc': resources.cached_teryt.simc,
    'terc': resources.cached_teryt.terc,
    'nts': resources.cached_teryt.nts
}
simc = Simc(simc_resource=params['simc'])
terc = Terc(terc_resource=params['terc'])
TerytField.translate_table = Terc(terc_resource=params['terc'])
nts = Nts(nts_resource=params['nts'])
