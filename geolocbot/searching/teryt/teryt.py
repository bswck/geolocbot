# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

""" Searching tool for TERYT register subsystems. """
# TODO: Fix ID fetcher common for NTS and TERC fields.

from geolocbot.tools import *
from geolocbot.libs import *
from geolocbot.auxiliary_types import *


__all__ = ('transferred_searches', 'terc', 'simc', 'nts')


class Teryt(object):
    def __repr__(self): return representation(type(self).__name__, **dict(self))

    def __iter__(self):
        for attrname in [attr for attr in self.__dict__.keys() if attr[:1] != '_']:
            yield attrname, getattr(self, attrname)


resources, _transferred_searches = geolocbot._resources, {}


def transferred_searches(name):
    for transfer in tuple(set(_transferred_searches.get(name, ()))):
        yield getattr(transfer, '_field_name'), transfer


class _Tools(Teryt):
    def fetch_col(self=Teryt):
        def decorator(meth: typing.Callable):
            def wrapper(*args, **kwargs):
                __self, col, df = self, kwargs['col'], kwargs['df']
                if isinstance(col, str):
                    ensure(hasattr(df, col), f'no column named {col!r}')
                    kwargs['col'] = df[col]
                return meth(*args, **kwargs)
            return wrapper
        return decorator

    fetch_col = fetch_col()

    @staticmethod
    @fetch_col
    @no_type_collisions
    def equal(*, df: pandas.DataFrame, col: (pandas.Series, str), value: (str, float), case: bool):
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
    @fetch_col
    @no_type_collisions
    def match(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.match(value, case=case))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @no_type_collisions
    def contains(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.contains(value, case=case, na=False))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @no_type_collisions
    def startswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.startswith(value, na=False)) \
            if case else \
            (col.str.lower().str.startswith(value.lower()))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @no_type_collisions
    def endswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
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
            search_mode: str,
            value_spaces: dict,
            case: bool,
            container_values: typing.Iterable,
            startswith_values: typing.Iterable,
            name_space_value: str = '',
    ):
        self.dataframe = dataframe
        self.field_name = field_name
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
        tools = _Tools

        def initial_search():
            self.candidate = getattr(tools, self.search_mode)(
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
        max_attempts = len(self.search_indicators)  # check this…
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
                    tools.contains(**stuff) if value_space in self.container_values else \
                    tools.startswith(**stuff) if value_space in self.startswith_values else \
                    tools.equal(**stuff)

                if self.failure():
                    if self.candidate.equals(self.dataframe):
                        anonymous_warning(f'It seems that all values in {value_space!r} value space are equal to '
                                          f'{query!r}. Try using more unique key words.', _category=FutureWarning)
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
    def __call__(self, search_indicators: dict):
        """ Wrapper for self._search(). """
        return self._search(search_indicators=search_indicators)


class TerytField(abstract_class, metaclass=better_abstract_metaclass):
    comparison_table = None
    fallback_comparison_table = None

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
            'args-assigned': 'cannot perform searching: please specify the arguments with their keys in the '
                             '\'key=value\' form, e.g.: search(startswith=\'a\')',
            'unknown-attr': 'couldn\'t fetch TERYT.%s',
            'subclass-is-none': 'field-representative subclass is None',
            'no-kwargs': 'cannot perform searching: no keyword arguments',
            'no-search-kwargs': 'no keyword arguments for searching (expected minimally 1 from: %s)',
            'empty-field': 'cannot instantiate _TerytEntry search with empty field. Happens mostly due to partially '
                           'intialized `loaders\' module. Please import `loaders\' before importing `filtering\'',
            'conflicting-kwargs': 'setting more than one keyword argument from %s in one search is impossible',
            'unexpected-kwarg-instance': 'got an unexpected type %r of parameter %r (expected type(s): %s)',
            'unexpected-kwarg': f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name '
                                f'in the following list:\n{" " * 12}%s.',
            'results': {'found': '[%s] Result(s):', 'not-found': '[%s] Entry frame not found.'},
            'more-than-one-entry': 'parser failed: cannot parse more than one TERYT entry (got %s entries)',
            'no-entry': 'parser failed: nothing to parse from',
            'not-teryt-subclass': 'cannot transfer search indicators not to TerytField subclass',
            'not-parsed-for-indicators': 'cannot perform getting indicators from properties if search results were not '
                                         'parsed (no parsed properties)',
            'not-a-value-space': f'%r is not a valid value space name. Available value spaces: %s.',
            'no-ids': '%r is not a %s',
            'empty-idtable': 'no ID table available for %s. Updating search indicators with the provided value, '
                             'however results are possible not to be found if it is not a valid ID.',
            'no-sfo': 'cannot evaluate subclass field object with provided name %r',
            'uncompvs': 'uncomparable value space: %r'
        }
        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, self._msgs['unknown-attr'] % self._field_name.lower())
        ensure(not self.field.empty, self._msgs['empty-field'])
        self._candidate = None
        self._container_values = ('function',)
        self._nametype_values = ('equal', 'match', 'startswith', 'endswith', 'contains')
        self._optbool_values = ('veinf', 'force_parse', 'parse', 'by_IDs', 'match_case', 'quiet')
        self._perr = geolocbot.exceptions.ParserError
        self._startswith_values = ('date',)
        self.case = None
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.conflicts = (self._nametype_values, ('force_parse', 'parse'))
        self.fparse, self.kwargs, self.name_space_value, self.parse = None, None, None, None
        self.search_indicators, self.search_kwargs, self.search_mode, self.veinf = None, None, None, None
        self.results_found = False
        self.parsed = False
        self._argid = {}
        self._argshed = {}
        self._sfo: TerytField = sub  # subclass field object
        self._gi_sfo = None  # subclass field object used for getting search indicators from local properties

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
        self._has_common_name = None  # (!) real value is assigned by parser(s)
        self._name = None  # (!) real value is assigned by parser(s)
        self._date = None  # (!) real value is assigned by parser(s)
        self._entry_frame = None  # (!) real value is assigned by parser(s)
        self._results = None  # (!) real value is assigned by parser(s)
        # End of single entry values

    def __repr__(self):
        return representation(
            self._field_name + '_field'
            if not self.parsed and not self.results_found
            else self._field_name + '_field' + '\n(*.results allows to fetch search results)'
            if self.results_found and not self.parsed
            else self._field_name + '_field_and_entry', **dict(self)
        )

    def __iter__(self):
        for value_space in self.value_spaces:
            if eval(f'self.{value_space!s}'):
                yield value_space, eval(f'self.{value_space!s}')

    def __del__(self):
        self.__init__(
            **{self._field_name.lower() + '_resource': self.field},
            field_name=self._field_name,
            sub=self
        )

    clear = __del__

    @abstractattribute
    def value_spaces(self): return {}

    @abstractattribute
    def comparable_value_spaces(self): return {}

    @property
    @underscored
    def level(self): return
    @level.deleter
    @underscored_deleter
    def level(self): return

    @property
    @underscored
    def region(self): return
    @region.deleter
    @underscored_deleter
    def region(self): return

    @property
    @underscored
    def subregion(self): return
    @subregion.deleter
    @underscored_deleter
    def subregion(self): return

    @property
    @underscored
    def voivodship(self): return
    @voivodship.deleter
    @underscored_deleter
    def voivodship(self): return

    @property
    @underscored
    def powiat(self): return
    @powiat.deleter
    @underscored_deleter
    def powiat(self): return

    @property
    @underscored
    def gmina(self): return
    @gmina.deleter
    @underscored_deleter
    def gmina(self): return

    @property
    @underscored
    def gmina_type(self): return
    @gmina_type.deleter
    @underscored_deleter
    def gmina_type(self): return

    @property
    @underscored
    def locality_type(self): return
    @locality_type.deleter
    @underscored_deleter
    def locality_type(self): return

    @property
    @underscored
    def has_common_name(self): return
    @has_common_name.deleter
    @underscored_deleter
    def has_common_name(self): return

    @property
    @underscored
    def name(self): return
    @name.deleter
    @underscored_deleter
    def name(self): return

    @property
    @underscored
    def function(self): return
    @function.deleter
    @underscored_deleter
    def function(self): return

    @property
    @underscored
    def id(self): return
    @id.deleter
    @underscored_deleter
    def id(self): return

    @property
    @underscored
    def integral_id(self): return
    @integral_id.deleter
    @underscored_deleter
    def integral_id(self): return

    @property
    @underscored
    def date(self): return
    @date.deleter
    @underscored_deleter
    def date(self): return

    @property
    @underscored
    def entry_frame(self): return
    @entry_frame.deleter
    @underscored_deleter
    def entry_frame(self): return

    @property
    @underscored
    def results(self): return pandas.DataFrame()
    @results.deleter
    @underscored_deleter
    def results(self): return

    def _gi_hook(self, _args, _kwargs):
        sfo_n = _args[0]
        ensure(all([sfo_n, not sfo_n.isspace(), globals().get(sfo_n) is not None]), self._msgs['no-sfo'] % sfo_n)
        self._gi_sfo = eval(f'{sfo_n!s}')
        ensure(issubclass(type(self._gi_sfo), TerytField), self._msgs['not-teryt-subclass'])
        ensure(self.parsed, self._msgs['not-parsed-for-indicators'])

    @no_type_collisions
    def _gids_hook(self, _args, _kwargs):
        ek, err = sorted(tuple(self.value_spaces.keys())), TypeError
        # 1. Check if all keyword args are expected
        [ensure(kwarg in ek, err(self._msgs['unexpected-kwarg'] % ('code', kwarg, ', '.join(ek)))) for kwarg in _kwargs]
        # 2. Separate arguments for ID getting and arguments for a direct search
        for kwn, kwv in _kwargs.items():
            if hasattr(IdTable, kwn + 's'):
                self._argid.update({kwn: kwv})
            self._argshed.update({kwn: kwv})  # don't lose the rest of arguments

    def _gnbid_hook(self, _args, _kwargs):
        if _args:
            value_space = _args[0]
            ensure(
                value_space in self.comparable_value_spaces,
                self._msgs['uncompvs'] % value_space
            )

    def _search_hook(self, _args, _kwargs):
        self.clear()
        key_words = _kwargs

        # 1. Check common conditions
        ensure(not _args, ValueError(self._msgs['args-assigned']))
        ensure(key_words, ValueError(self._msgs['no-kwargs']))

        # 2. Check if arguments and their types are expected
        self.search_kwargs = self._nametype_values + tuple(self.value_spaces.keys())
        self.kwargs = self.search_kwargs + self._optbool_values
        for kwarg, value in key_words.items():
            ensure(
                kwarg in self.kwargs, ValueError(self._msgs['unexpected-kwarg'] % ('search', kwarg, ', '.join(
                    sorted(self.kwargs))))
            )
            expected_instance = bool if kwarg in self._optbool_values else (str, IdName)
            unexpected_instance = 'search() ' + self._msgs['unexpected-kwarg-instance'] % (
                type(value).__name__, kwarg, ', '.join(
                            [f'{obj_type.__name__!r}' for obj_type in expected_instance]
                        ) if isinstance(expected_instance, typing.Iterable) else type(expected_instance).__name__
            )
            if isinstance(value, IdName):
                key_words[kwarg] = str(value)
            ensure(isinstance(value, expected_instance), TypeError(unexpected_instance))

        # 3. Check if any search keyword arg has been provided
        ensure(
            any([kwarg in key_words for kwarg in self.search_kwargs]),
            ValueError(self._msgs['no-search-kwargs'] % ', '.join(sorted(self.search_kwargs)))
        )

        # 4. Handle conflicts
        for conflicted in self.conflicts:
            conflict = []
            for arg in conflicted:
                if arg in key_words:
                    formatter = ' and '.join([f'\'{x!s}=…\'' for x in conflicted])
                    ensure(not conflict, self._msgs['conflicting-kwargs'] % formatter)
                    conflict.append(arg)

        self.name_space_value, self.fparse = None, True
        modes = self._nametype_values + ('no_name_col',)
        self.search_mode = modes[-1]

        # 5. Get the search mode and 'name' value-space value
        for kwarg in key_words.copy():
            for mode in self._nametype_values:
                if kwarg == mode:
                    self.search_mode, self.name_space_value = mode, key_words[mode]
                    del key_words[mode]

        # 6. Pop the boolean options
        self.veinf = key_words.pop('veinf', False)
        if key_words.pop('quiet', False) and not geolocbot.tools.be_quiet:
            self.quiet = True
            geolocbot.tools.be_quiet = self.quiet
        self.parse = key_words.pop('parse', True)
        self.fparse, self.case = key_words.pop('force_parse', False), key_words.pop('match_case', False)
        self.by_IDs = key_words.pop('by_IDs', False)

        # 7. Set the search indicators
        if not self.by_IDs:
            key_words = self._get_ids_by_names(**key_words)
        self.search_indicators = key_words

        self._candidate, frames = self.field.copy(), [self.field.copy()]

        for value_space in self.search_indicators:
            _col = self.value_spaces[value_space]
            self.field[_col] = self.field[self.value_spaces[value_space]].map(str)  # map all to strings

        return True

    @hook(_gids_hook)
    def _get_ids_by_names(self, **_kwargs):
        id_indicators = {**self._argshed}
        spaces = list(self.value_spaces.keys())
        for value_space, value in self._argid.items():
            plural = value_space + 's'
            id_dataframe = getattr(IdTable, plural)

            if id_dataframe.empty:
                anonymous_warning(self._msgs['empty-idtable'] % plural)
                id_indicators.update({value_space: value})
                continue

            entry = _FieldSearch(
                dataframe=id_dataframe,
                field_name=getattr(self.comparison_table, '_field_name'),
                search_mode='equal',
                value_spaces=self.value_spaces,
                case=False,
                container_values=self._container_values,
                startswith_values=self._startswith_values,
                name_space_value=value
            )(search_indicators=id_indicators)

            ensure(not entry.empty, self._msgs['no-ids'] % (value, value_space))
            id_indicators.update({value_space: entry.iat[0, entry.columns.get_loc(self.value_spaces[value_space])]})

            if value_space != spaces[0]:
                quantum = spaces.index(value_space) - 1
                for rot in range(quantum + 1):
                    prev_ = spaces[quantum - rot]
                    id_indicators[prev_] = entry.iat[0, entry.columns.get_loc(self.value_spaces[prev_])]

        return id_indicators

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
            self.results_found = True
            output(self._msgs['results']['found'] % self._field_name, self._candidate, sep='\n')
            self._results = self._candidate.reset_index()
            if (len(self._candidate) == 1 or self.fparse) and self.parse:
                self.parse_entry()
            return self._sfo

    @hook(_gnbid_hook)
    @no_type_collisions
    def _get_name_by_id(self, value_space: str, value: str):
        comparison_table = self.comparison_table \
            if value_space in self.comparison_table.value_spaces \
            else self.fallback_comparison_table \
            if value_space in self.fallback_comparison_table.value_spaces \
            else do_nothing()

        if comparison_table is None or value_space not in self.comparable_value_spaces:
            return ''

        indicators = {'function': self.value_spaces[value_space]}  # e.g. 'woj' will match 'województwo' etc.
        spaces = list(self.value_spaces.keys())

        if value_space != spaces[0]:
            quantum = spaces.index(value_space) - 1
            for rot in range(quantum + 1):
                prev_ = spaces[quantum - rot]
                indicators[prev_] = str(getattr(self, '_' + prev_))

        indicators[value_space] = value

        if value_space != spaces[-1]:
            next_ = spaces[spaces.index(value_space) + 1]
            indicators[next_] = 'nan'

        comparison_dataframe = _FieldSearch(
            dataframe=comparison_table.field,
            field_name=getattr(comparison_table, '_field_name'),
            search_mode='no_name_col',
            value_spaces=comparison_table.value_spaces,
            case=False,
            container_values=getattr(comparison_table, '_container_values'),
            startswith_values=getattr(comparison_table, '_startswith_values'),
        )(search_indicators=indicators)

        return comparison_dataframe.iat[0, comparison_dataframe.columns.get_loc(comparison_table.value_spaces['name'])]

    def failure(self):
        return self._candidate.empty or self._candidate.equals(self.field)


    @hook(_gi_hook)
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
        indicators = {**properties, 'by_IDs': True, 'equal': name_space_value, 'veinf': self.veinf,
                      'force_parse': self.fparse, 'match_case': self.case}
        yield indicators
        yield sfo

    @abstractmethod
    def fetch_id(self):
        pass

    @no_type_collisions
    def parse_entry(self, dataframe: pandas.DataFrame = None) -> "type(None)":
        dataframe, value_spaces = dataframe if dataframe is not None else self.results, self.value_spaces
        ensure(not dataframe.empty, self._perr(self._msgs['no-entry']))
        ensure(len(dataframe) == 1, self._perr(self._msgs['more-than-one-entry'] % len(dataframe)))
        self._entry_frame = dataframe

        for value_space, real_value in value_spaces.items():
            value = dataframe.iat[0, dataframe.columns.get_loc(real_value)]
            if value != 'nan':
                setattr(
                    self, '_' + value_space,
                    IdName(id_=value, name=self._get_name_by_id(value_space, value))
                    if value_space in self.comparable_value_spaces
                    else value
                )

        self.fetch_id()
        self.parsed = True
        return self._sfo

    # @reraise(geolocbot.exceptions.SearchError)  ← TODO
    @hook(_search_hook)
    def search(self, *_args, **_kwargs) -> "TerytField":
        self._candidate = _FieldSearch(
            dataframe=self.field,
            field_name=self._field_name,
            search_mode=self.search_mode,
            value_spaces=self.value_spaces,
            case=self.case,
            name_space_value=self.name_space_value,
            container_values=self._container_values,
            startswith_values=self._startswith_values
        )(search_indicators=self.search_indicators)
        return self._results_handler()

    def listing(self, value_space, parse=True):
        dataframe = self.results.copy() if self.results_found else self.field.copy()
        ensure(
            value_space in self.value_spaces,
            self._msgs['not-a-value-space'] % (value_space, ', '.join(sorted(list(self.value_spaces.keys()))))
        )
        list_ = sorted(getattr(dataframe, self.value_spaces[value_space]).tolist())
        if parse:
            for keyind in range(len(list_)):
                self.parse_entry(dataframe=pandas.DataFrame([dataframe.loc[dataframe.index[keyind]]]))
                # TODO: cleaning after auxiliary parsing
                if value_space in self.comparable_value_spaces:
                    list_[keyind] = IdName(
                        id_=list_[keyind],
                        name=self._get_name_by_id(value_space=value_space, value=list_[keyind])
                    )
        return list_

    def mapping(self, parse=True):
        results = self.results.copy()  # don't lose the results, they'll be "cleaned"
        for value_space in self.value_spaces:
            yield value_space, tuple(self.listing(value_space, parse=parse))
        self.clear()
        self._results = results

    @no_type_collisions
    def transfer(self, sfo_name: str) -> "TerytField":
        stuff, sfo = self.get_indicators(sfo_name)
        global _transferred_searches
        _transferred_searches[stuff['equal']] = \
            _transferred_searches.pop(stuff['equal'], ()) + (self, sfo.search(**stuff))
        return _transferred_searches[stuff['equal']][-1]


class Terc(TerytField):
    def __init__(self, terc_resource, *_args, **_kwargs):
        super(Terc, self).__init__(field_name='terc', sub=self, terc_resource=terc_resource)
        TerytField.comparison_table = self
        self.value_spaces = {
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ',
            'name': 'NAZWA',
            'function': 'NAZWA_DOD',
            'date': 'STAN_NA',
        }
        self.comparable_value_spaces = \
            (
                'voivodship',
                'powiat',
                'gmina',
                'gmina_type',
            )

    def fetch_id(self) -> "TerytField":
        self._id = ''.join([str(getattr(self, id_)) for id_ in self.value_spaces if hasattr(IdTable, id_)])
        return self


class Simc(TerytField):
    def __init__(self, simc_resource, *_args, **_kwargs):
        super(Simc, self).__init__(field_name='simc', sub=self, simc_resource=simc_resource)
        self.value_spaces = {
            'voivodship': 'WOJ',
            'powiat': 'POW',
            'gmina': 'GMI',
            'gmina_type': 'RODZ_GMI',
            'locality_type': 'RM',
            'has_common_name': 'MZ',
            'name': 'NAZWA',
            'id': 'SYM',
            'integral_id': 'SYMPOD',
            'date': 'STAN_NA',
        }
        self.comparable_value_spaces = \
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
    def __init__(self, nts_resource, *_args, **_kwargs):
        super(Nts, self).__init__(field_name='nts', sub=self, nts_resource=nts_resource)
        TerytField.fallback_comparison_table = self
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
        self.comparable_value_spaces = \
            (
                'region',
                'voivodship',
                'subregion',
                'powiat',
                'gmina',
                'gmina_type',
            )

    def fetch_id(self) -> "TerytField":
        self._id = ''.join([str(getattr(self, id_)) for id_ in self.value_spaces if hasattr(IdTable, id_)])
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


class _IdTable(Teryt):
    def __init__(self):
        self.tt = TerytField.comparison_table
        self.ft = TerytField.fallback_comparison_table
        self.levels = pandas.DataFrame()  # symbolic
        self.regions = self.ft.search(function='^region', by_IDs=True, quiet=True).results
        self.subregions = self.ft.search(function='podregion', by_IDs=True, quiet=True).results
        self.voivodships = self.tt.search(function='województwo', by_IDs=True, quiet=True).results
        self.powiats = self.tt.search(function='powiat', by_IDs=True, quiet=True).results
        self.gminas = self.tt.search(function='gmina', by_IDs=True, quiet=True).results
        self.tt.clear()
        self.ft.clear()


IdTable = Teryt  # (!) real value is: _IdTable()
