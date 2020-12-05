# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from geolocbot.tools import *
from geolocbot.libs import *

subsystems = ('simc', 'terc', 'nts')
nim_initd = False
__all__ = ('transferred_searches', *subsystems)


class Teryt:
    def __repr__(self): return representation(type(self).__name__, **dict(self))

    def __iter__(self):
        for attrname in [attr for attr in self.__dict__.keys() if attr[:1] != '_']:
            yield attrname, getattr(self, attrname)


class NameID(Teryt):
    @typecheck
    def __init__(self, name: (str, bool) = '', id_: str = ''):
        self.name = name
        self.ID = id_

    def __getitem__(self, item): return getattr(self, item, '')

    def __repr__(self): return 'Name&ID(' + ', '.join(['%s=%r' % (k, v) for k, v in dict(self).items()]) + ')'

    def __str__(self): return str(self.ID) if self.ID else ''

    def __add__(self, other): return str(self.ID) if self else '' + other

    def __bool__(self): return all([self.name, str(self.ID) != 'nan'])

    def __iter__(self):
        if self.name:
            yield 'name', self.name
        yield 'ID', self.ID


resources, _transferred_searches = geolocbot._resources, {}


def transferred_searches(name):
    for transfer in tuple(set(_transferred_searches.get(name, ()))):
        yield getattr(transfer, '_field_name'), transfer


class _TFSearchTools(Teryt):
    def fetch_col(self=Teryt):
        def decorator(meth: typing.Callable):
            def wrapper(*args, **kwargs):
                __self, col, df = self, kwargs['col'], kwargs['df']
                if isinstance(col, str):
                    ensure(col in df.columns, f'no column named {col!r}')
                    kwargs['col'] = df[col]
                return meth(*args, **kwargs)

            return wrapper

        return decorator

    fetch_col = fetch_col()

    @staticmethod
    @fetch_col
    @typecheck
    def name(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col == value) \
                if case else \
                (col.str.lower() == str(value).lower())
        return df.loc[query]

    equal = name

    @staticmethod
    @fetch_col
    @typecheck
    def match(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.match(value, case=case))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @typecheck
    def contains(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.contains(value, case=case, na=False))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @typecheck
    def startswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.startswith(value, na=False)) \
                if case else \
                (col.str.lower().str.startswith(value.lower()))
        return df.loc[query]

    @staticmethod
    @fetch_col
    @typecheck
    def endswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.endswith(value, na=False)) \
                if case else \
                (col.str.lower().str.endswith(value.lower(), na=False))
        return df.loc[query]

    def __repr__(self): return representation('SearchingTools')


class _TFSearch(Teryt):
    @typecheck
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
        inef_ki = keys.index(self.ineffective_value_space)
        inef_value = values[inef_ki]
        del keys[inef_ki], values[inef_ki]
        keys.insert(inef_ki + 1, self.ineffective_value_space)
        values.insert(inef_ki + 1, inef_value)
        self.search_indicators = dict(zip(keys, values))
        return self.search_indicators

    def _search(self, search_indicators):
        self.candidate = self.dataframe.copy()
        self.search_indicators = search_indicators
        value_spaces = self.value_spaces
        self.frames = [self.candidate]
        tools = _TFSearchTools

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
        max_attempts = len(self.search_indicators) ** 2
        done = False

        def search_loop():
            nonlocal self, attempts, done
            for value_space, query in self.search_indicators.items():
                attempts += 1
                if value_space in self.value_spaces:
                    col = self.value_spaces[value_space]
                else:  # TODO
                    continue
                stuff = dict(df=self.candidate, col=col, value=query, case=self.case)
                self.candidate = \
                    tools.contains(**stuff) if value_space in self.container_values else \
                    tools.startswith(**stuff) if value_space in self.startswith_values else \
                    tools.name(**stuff)

                if self.failure():
                    if self.candidate.equals(self.dataframe):
                        anonymous_warning(f'It seems that all values in {value_space!r} value space are equal to '
                                          f'{query!r}. Try using more unique key words.')
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

    @typecheck
    def __call__(self, search_indicators: dict):
        """ Wrapper for self._search(). """
        return self._search(search_indicators=search_indicators)


class TF(ABC, metaclass=bABCMeta):
    TercNIM = None
    NtsNIM = None

    def __init__(
            self,
            *,
            field_name: str,
            sub,
            simc_resource=resources.cached_teryt.simc,
            terc_resource=resources.cached_teryt.terc,
            nts_resource=resources.cached_teryt.nts
    ):
        ensure(nim_initd, 'cannot instantiate TERYT field: _IdNameMap was not initialized!')
        self._invalid_kwd_msg = \
            f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name ' \
            f'in the following list:\n{" " * 12}%s.'
        self._r_not_s = '%r is not a %s'
        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        ensure(self.field is not None, f'couldn\'t fetch searching.teryt.{self._field_name.lower()}')
        ensure(not self.field.empty,'cannot instantiate _TFSearch with an empty field')
        self._candidate = None  # auxiliary
        self._container_values = ('function',)  # auxiliary
        self._name_value_space_kwds = ('name', 'match', 'startswith', 'endswith', 'contains')  # auxiliary
        self._bool_optional = ('veinf', 'force_parse', 'parse', 'by_IDs', 'match_case')  # auxiliary
        self._str_optional = ('terid',)  # auxiliary
        self._other_kwds = self._bool_optional + self._str_optional  # auxiliary
        self._perr = geolocbot.exceptions.ParserError  # auxiliary
        self._startswith_values = ('date',)  # auxiliary
        self.case = None
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.columns = self.cols
        self.conflicts = (self._name_value_space_kwds, ('force_parse', 'parse'))
        self.fparse, self._valid_kwds, self.name_value_space, self.parse = None, None, None, None
        self.search_indicators, self._search_only_kwds, self.search_mode, self.veinf = None, None, None, None
        self.results_found = False
        self.parsed = False
        self._argid = {}  # auxiliary
        self._argshed = {}  # auxiliary
        self._sfo: TF = sub  # subclass field object
        self._gi_sfo = None  # subclass field object used for getting search indicators from local properties

        # Single entry values
        self._terid = None  # (!) real value is assigned by parser(s)
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
        self._loctype = None  # (!) real value is assigned by parser(s)
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
        if getattr(self, 'terid'):
            yield 'terid', getattr(self, 'terid')
        for value_space in self.value_spaces:
            if getattr(self, value_space):
                yield value_space, getattr(self, value_space)

    def __del__(self):
        self.__init__(
            **{self._field_name.lower() + '_resource': self.field},
            field_name=self._field_name,
            sub=self
        )

    clear = __del__

    @abstractAttribute
    def value_spaces(self):
        return {}

    @abstractAttribute
    def dfnim_value_spaces(self):
        return {}

    @property
    @underscored
    def terid(self):
        return ''

    @terid.deleter
    @underscored_deleter
    def terid(self):
        return

    @property
    @underscored
    def level(self):
        return ''

    @level.deleter
    @underscored_deleter
    def level(self):
        return

    @property
    @underscored
    def region(self):
        return ''

    @region.deleter
    @underscored_deleter
    def region(self):
        return

    @property
    @underscored
    def subregion(self):
        return ''

    @subregion.deleter
    @underscored_deleter
    def subregion(self):
        return

    @property
    @underscored
    def voivodship(self):
        return ''

    @voivodship.deleter
    @underscored_deleter
    def voivodship(self):
        return

    @property
    @underscored
    def powiat(self):
        return ''

    @powiat.deleter
    @underscored_deleter
    def powiat(self):
        return

    @property
    @underscored
    def gmina(self):
        return ''

    @gmina.deleter
    @underscored_deleter
    def gmina(self):
        return

    @property
    @underscored
    def gmina_type(self):
        return ''

    @gmina_type.deleter
    @underscored_deleter
    def gmina_type(self):
        return

    @property
    @underscored
    def loctype(self):
        return ''

    @loctype.deleter
    @underscored_deleter
    def loctype(self):
        return

    @property
    @underscored
    def has_common_name(self):
        return ''

    @has_common_name.deleter
    @underscored_deleter
    def has_common_name(self):
        return

    @property
    @underscored
    def name(self):
        return ''

    @name.deleter
    @underscored_deleter
    def name(self):
        return

    @property
    @underscored
    def function(self):
        return ''

    @function.deleter
    @underscored_deleter
    def function(self):
        return

    @property
    @underscored
    def id(self):
        return ''

    @id.deleter
    @underscored_deleter
    def id(self):
        return

    @property
    @underscored
    def integral_id(self):
        return ''

    @integral_id.deleter
    @underscored_deleter
    def integral_id(self):
        return

    @property
    @underscored
    def date(self):
        return ''

    @date.deleter
    @underscored_deleter
    def date(self):
        return

    @property
    @underscored
    def entry_frame(self):
        return pandas.DataFrame()

    @entry_frame.deleter
    @underscored_deleter
    def entry_frame(self):
        return

    @property
    @underscored
    def results(self):
        return pandas.DataFrame()

    @results.deleter
    @underscored_deleter
    def results(self):
        return

    @typecheck
    def _has_dict_nim(self, value_space: str) -> "bool":
        """ Check if *self* has dict-type attribute standing for value space's comparison table. """
        return hasattr(self, value_space + '_nim')

    @typecheck
    def _has_df_nim(self, value_space: str) -> "bool":
        """ Check if *self* has DataFrame-type attribute standing for value space's comparison table. """
        return value_space in self.dfnim_value_spaces

    @typecheck
    def _has_nim(self, value_space: str) -> "bool":
        """ Check if *self* is comparable in any of comparison tables. """
        return self._has_dict_nim(value_space) or self._has_df_nim(value_space)

    # ---- Preceding methods
    def __generate_indicators(self, _args, _kwargs):
        """ Precede self.generate_indicators(). """
        ensure(_args, 'generate_indicators(): no args')
        sfo_name = _args[0]
        ensure(
            all([sfo_name, not sfo_name.isspace(), globals().get(sfo_name) is not None]),
            f'cannot evaluate subclass field object with provided name {sfo_name!r}'
        )
        self._gi_sfo = eval(f'{sfo_name!s}')()
        ensure(issubclass(type(self._gi_sfo), TF), 'cannot transfer search indicators not to TerytField subclass')
        ensure(
            self.parsed,
            'cannot perform generating indicators from properties if search results were not parsed'
        )

    def __get_ids_by_names(self, _args, _kwargs):
        """ Precede self._get_ids_by_names(). """
        valid_kwds = sorted(tuple(self.value_spaces.keys()))
        # 1. Check if all keyword arguments are expected
        [ensure(
            kwd in valid_kwds, 
            TypeError(self._invalid_kwd_msg % ('_get_ids_by_names', kwd, ', '.join(valid_kwds)))
        ) for kwd in list(set(_kwargs))]
        
        # 2. Separate arguments for ID getting and arguments for direct search
        for name, value in _kwargs.items():
            if self._has_df_nim(name):
                self._argid |= {name: value}
                continue
            elif self._has_dict_nim(name):
                nim = getattr(self, name + '_nim')
                ensure(value in nim, self._r_not_s % (value, f'valid \'{name.replace("_", " ")}\' non-ID value'))
                self._argshed |= {name: nim[value]}  # don't lose the other arguments

    def __get_name_by_id(self, _args, _kwargs):
        """ Precede self._get_name_by_id(). """
        if _args:
            value_space = _args[0]
            ensure(self._has_nim(value_space), f'value space {value_space!r} does not have a name-ID map')

    def __search(self, _args, _kwargs):
        """ Precede self.search(). """
        self.clear()
        keywords = _kwargs

        # 1. Check common conditions
        ensure(
            not _args,
            ValueError(
                'cannot perform searching: please specify the arguments with their keys in the \'key=value\' '
                'form, e.g.: search(startswith=\'a\')')
        )
        ensure(keywords, ValueError('cannot perform searching: no keyword arguments'))

        # 2. Check if arguments and their types are expected
        self._search_only_kwds = tuple(
            set(self._name_value_space_kwds + tuple(self.value_spaces.keys()))
        ) + self._str_optional
        self._valid_kwds = self._search_only_kwds + self._other_kwds
        for keyword, value in keywords.items():
            ensure(
                keyword in self._valid_kwds,
                ValueError(self._invalid_kwd_msg % (
                    'search', keyword, ', '.join(sorted(set(self._valid_kwds)))
                ))
            )
            valid_type = (bool,) if keyword in self._bool_optional or keyword.startswith('has') else (str, NameID)
            str_valid_types = (', '.join([repr(_type.__name__) for _type in valid_type])
                               if isinstance(valid_type, typing.Iterable) else type(valid_type).__name__)
            invalid_type_msg = f'search() got an unexpected type {type(value).__name__!r} of parameter ' \
                               f'{keyword!r} (expected type(s): %s)' % str_valid_types
            if isinstance(value, NameID):
                keywords[keyword] = str(value)
            ensure(isinstance(value, valid_type), TypeError(invalid_type_msg))

        # 3. Check if any search keyword argument has been provided
        ensure(
            any([keyword in keywords for keyword in self._search_only_kwds]),
            ValueError(
                f'no keyword arguments for searching (expected minimally 1 from: '
                f'{", ".join(sorted(self._search_only_kwds))})'
            )
        )

        self.conflicts += tuple(('terid', nim_value_space) for nim_value_space in self.dfnim_value_spaces)

        # 4. Handle conflicts
        for conflicted in self.conflicts:
            conflict = []
            for argument in conflicted:
                if argument in keywords:
                    ensure(
                        not conflict,
                        'setting more than one keyword argument from %s in one search is impossible' %
                        ' and '.join([f'\'{conflicted_arg!s}=…\'' for conflicted_arg in sorted(conflicted)])
                    )
                    conflict.append(argument)

        self.name_value_space, self.fparse = None, True
        modes = self._name_value_space_kwds + ('no_name_col',)
        self.search_mode = modes[-1]

        # 5. Get the search mode and 'name' value space value
        for keyword in keywords.copy():
            for mode in self._name_value_space_kwds:
                if keyword == mode:
                    self.search_mode, self.name_value_space = mode, keywords[mode]
                    del keywords[mode]

        # 6. Pop stuff
        self.veinf = keywords.pop('veinf', False)
        self.parse = keywords.pop('parse', True)
        self.fparse, self.case = keywords.pop('force_parse', False), keywords.pop('match_case', False)
        self.by_IDs = keywords.pop('by_IDs', False)
        terid = keywords.pop('terid', '')

        # 7. Set the search indicators
        if not self.by_IDs:
            keywords = self._get_ids_by_names(**keywords)
        if terid:
            dispatched = self.dispatch_terid(terid)
            [keywords.__setitem__(n, v) for n, v in dispatched.items() if v]

        self.search_indicators = keywords

        self._candidate, frames = self.field.copy(), [self.field.copy()]

        for value_space in self.search_indicators:
            _col = self.value_spaces[value_space]
            self.field[_col] = self.field[self.value_spaces[value_space]].map(str)  # map all to strings

        return True

    # ----------

    @called_after(__get_ids_by_names)
    def _get_ids_by_names(self, **_kwargs):
        id_indicators = {**self._argshed}
        for value_space in self._argshed.keys():
            if value_space not in self.TercNIM.columns:
                id_indicators.pop(value_space)

        spaces = list(self.value_spaces.keys())
        for value_space, value in self._argid.items():
            plural_name = value_space + 's'
            id_dataframe = getattr(NameIDMap, plural_name)

            if id_dataframe.empty:
                anonymous_warning(
                    f'no name-ID map available for {plural_name}. Updating search indicators with the provided value, '
                    f'however results are possible not to be found if it is not a valid ID.'
                )
                id_indicators |= {value_space: value}
                continue

            entry = _TFSearch(
                dataframe=id_dataframe,
                field_name=getattr(self.TercNIM, '_field_name'),
                search_mode='equal',
                value_spaces=self.value_spaces,
                case=False,
                container_values=self._container_values,
                startswith_values=self._startswith_values,
                name_space_value=value
            )(search_indicators=id_indicators)

            ensure(not entry.empty, self._r_not_s % (value, value_space))
            id_indicators |= {value_space: entry.iat[0, entry.columns.get_loc(self.value_spaces[value_space])]}

            if value_space != spaces[0]:
                quantum = spaces.index(value_space) - 1
                for rot in range(quantum + 1):
                    prev = spaces[quantum - rot]
                    id_indicators[prev] = entry.iat[0, entry.columns.get_loc(self.value_spaces[prev])]
        return {**id_indicators, **self._argshed}

    def __handle_results(self):
        """ Handle results. """
        if self.failure():
            def _hf():
                """ Handle failure. """
                self.__del__()
                ensure(not self.veinf, 'no results found')
                return self._sfo
            return _hf()
        else:
            self.results_found = True
            self._results = self._candidate.reset_index()
            if (len(self._candidate) == 1 or self.fparse) and self.parse:
                self.parse_entry()
            return self._sfo

    @called_after(__get_name_by_id)
    @typecheck
    def _get_name_by_id(self, value_space: str, value: str):
        if self._has_dict_nim(value_space):
            return rev_dict(getattr(self, value_space + '_nim'))[value]

        tfnim = self.TercNIM \
            if value_space in self.TercNIM.value_spaces \
            else self.NtsNIM \
            if value_space in self.NtsNIM.value_spaces \
            else do_nothing()

        if any([tfnim is None, value_space not in self.dfnim_value_spaces, value is nan]):
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

        comparison_dataframe = _TFSearch(
            dataframe=tfnim.field,
            field_name=getattr(tfnim, '_field_name'),
            search_mode='no_name_col',
            value_spaces=tfnim.value_spaces,
            case=False,
            container_values=getattr(tfnim, '_container_values'),
            startswith_values=getattr(tfnim, '_startswith_values'),
        )(search_indicators=indicators)

        return comparison_dataframe.iat[0, comparison_dataframe.columns.get_loc(tfnim.value_spaces['name'])]

    def failure(self):
        return self._candidate.empty or self._candidate.equals(self.field)

    @called_after(__generate_indicators)
    @typecheck
    def generate_indicators(self, _sfo_name: str):
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
        indicators = {**properties, 'by_IDs': True, 'name': name_space_value, 'veinf': self.veinf,
                      'force_parse': self.fparse, 'match_case': self.case}
        yield indicators
        yield sfo

    def set_terid(self) -> "TF":
        """ Common and default for all subsystems. """
        self._terid = ''.join(
            [str(getattr(self, tid)) for tid in self.dfnim_value_spaces if str(getattr(self, tid)) != 'nan']
        )
        return self

    @typecheck
    def dispatch_terid(self, teritorial_id: str, errors: bool = True):
        ensure(teritorial_id, 'teritorial ID to be dispatched cannot be an empty string')
        code_indicators = {}
        frames = {}
        max_len = sum(list(self.dfnim_value_spaces.values()))
        ensure(
            len(teritorial_id) <= max_len,
            f'{self._field_name.upper()} '
            f'teritorial ID length is expected to be {max_len}'
        )
        index = 0

        for dnvs, valid_length in self.dfnim_value_spaces.items():
            if index >= len(teritorial_id) - 1:
                break
            frames |= {dnvs: getattr(NameIDMap, dnvs + 's')}
            part = teritorial_id[index:index + valid_length]
            if errors:
                ensure(
                    not self.search(by_IDs=True, parse=False, **{dnvs: part}).results.empty,
                    'dispatch_teritorial_id(…, errors=True, …): ' + self._r_not_s % (
                        '…' + part,
                        f'valid teritorial ID part (error at {dnvs!r} value space, col {self.value_spaces[dnvs]!r})'
                    )
                )
            code_indicators |= {dnvs: part}
            index += valid_length

        return code_indicators

    @typecheck
    def parse_entry(self, dataframe: pandas.DataFrame = None):
        dataframe, value_spaces = dataframe if dataframe is not None else self.results, self.value_spaces
        ensure(not dataframe.empty, self._perr('parser failed: nothing to parse from'))
        ensure(
            len(dataframe) == 1,
            self._perr(f'parser failed: cannot parse more than one TERYT entry (got {len(dataframe)} entries)')
        )
        for value_space in value_spaces:
            ensure(
                value_spaces[value_space] in dataframe,
                self._perr(
                    f'parser failed: value space {value_space} '
                    f'(the real column is named {value_spaces[value_space]}) not in source DataFrame'
                )
            )
        self._entry_frame = dataframe

        for value_space, real_value in value_spaces.items():
            value = dataframe.iat[0, dataframe.columns.get_loc(real_value)]
            if value != 'nan':
                setattr(
                    self, '_' + value_space,
                    NameID(id_=value, name=self._get_name_by_id(value_space, value))
                    if self._has_nim(value_space)
                    else value
                )

        self.set_terid()
        self.parsed = True
        return self._sfo

    # @reraise(geolocbot.exceptions.SearchError)  ← TODO
    @called_after(__search)
    def search(self, *_args, **_kwargs) -> "TF":
        self._candidate = _TFSearch(
            dataframe=self.field,
            field_name=self._field_name,
            search_mode=self.search_mode,
            value_spaces=self.value_spaces,
            case=self.case,
            name_space_value=self.name_value_space,
            container_values=self._container_values,
            startswith_values=self._startswith_values
        )(search_indicators=self.search_indicators)
        return self.__handle_results()

    def to_list(self, value_space, parse=True) -> "list":
        dataframe = self.field.copy() if not self.results_found else self.results.copy()
        ensure(
            value_space in self.value_spaces,
            f'{value_space!r} is not a valid value space name. Available value spaces: '
            f'{", ".join(sorted(list(self.value_spaces.keys())))}'
        )
        lst = getattr(dataframe, self.value_spaces[value_space]).tolist()
        if parse and self._has_nim(value_space):
            for ki in range(len(lst)):
                self.parse_entry(dataframe=pandas.DataFrame([dataframe.loc[dataframe.index[ki]]]))
                # TODO: cleaning after parsing (which is in fact auxiliary)
                lst[ki] = NameID(
                    id_=lst[ki],
                    name=self._get_name_by_id(value_space=value_space, value=lst[ki])
                )
        return lst

    def to_dict(self, parse=True) -> "dict":
        results = self.results.copy()  # don't lose current results, they'll be deleted
        dct = {}
        for value_space in self.value_spaces:
            value = tuple(self.to_list(value_space, parse=parse))
            dct |= {value_space: value[0] if len(value) == 1 else value}
        self.clear()
        self._results = results
        return dct

    @typecheck
    def transfer(self, sfo_name: str) -> "TF":
        stuff, sfo = self.generate_indicators(sfo_name)
        global _transferred_searches
        _transferred_searches[stuff['name']] = \
            _transferred_searches.pop(stuff['name'], ()) + (self, sfo.search(**stuff))
        return _transferred_searches[stuff['name']][-1]


class Terc(TF):
    def __init__(self, terc_resource=resources.cached_teryt.terc, *_args, **_kwargs):
        super(Terc, self).__init__(field_name='terc', sub=self, terc_resource=terc_resource)
        TF.TercNIM = self
        self.value_spaces = {
            'voivodship': 'WOJ', 'powiat': 'POW', 'gmina': 'GMI', 'gmina_type': 'RODZ', 'name': 'NAZWA',
            'function': 'NAZWA_DOD', 'date': 'STAN_NA',
        }
        self.dfnim_value_spaces = {'voivodship': 2, 'powiat': 2, 'gmina': 2, 'gmina_type': 1}


class Simc(TF):
    def __init__(self, simc_resource=resources.cached_teryt.simc, *_args, **_kwargs):
        super(Simc, self).__init__(field_name='simc', sub=self, simc_resource=simc_resource)
        self.value_spaces = {
            'voivodship': 'WOJ', 'powiat': 'POW', 'gmina': 'GMI', 'gmina_type': 'RODZ_GMI', 'loctype': 'RM',
            'has_common_name': 'MZ', 'name': 'NAZWA', 'id': 'SYM', 'integral_id': 'SYMPOD', 'date': 'STAN_NA'
        }
        self.loctype_nim = {  # hierarchized
            'miasto': '96',
            'delegatura': '98',
            'dzielnica m. st. Warszawy': '95',
            'część miasta': '99',
            'wieś': '01',
            'przysiółek': '03',
            'kolonia': '02',
            'osada': '04',
            'osada leśna': '05',
            'osiedle': '06',
            'schronisko turystyczne': '07',
            'część miejscowości': '00',
        }
        # ↑ See: https://bit.ly/2VqfxMG ('SIMC' tab)
        self.has_common_name_nim = {True: '1', False: '0'}
        self.dfnim_value_spaces = {'voivodship': 2, 'powiat': 2, 'gmina': 2, 'gmina_type': 1}


class Nts(TF):
    # TODO: check for NIM of levels
    def __init__(self, nts_resource=resources.cached_teryt.nts, *_args, **_kwargs):
        super(Nts, self).__init__(field_name='nts', sub=self, nts_resource=nts_resource)
        TF.NtsNIM = self
        self.value_spaces = {
            'level': 'POZIOM', 'region': 'REGION', 'voivodship': 'WOJ', 'subregion': 'PODREG', 'powiat': 'POW',
            'gmina': 'GMI', 'gmina_type': 'RODZ', 'name': 'NAZWA', 'function': 'NAZWA_DOD', 'date': 'STAN_NA'
        }
        self.dfnim_value_spaces = {
            'region': 1, 'voivodship': 2, 'subregion': 2, 'powiat': 2, 'gmina': 2, 'gmina_type': 1
        }

    @typecheck
    def dispatch_terid(self, teritorial_id: str, errors: bool = True):
        ensure(teritorial_id, 'teritorial ID to be dispatched cannot be an empty string')
        level = teritorial_id[0]
        if errors:
            ensure(
                not self.search(by_IDs=True, parse=False, **{'level': level}).results.empty,
                'dispatch_teritorial_id(…, errors=True, …): ' + self._r_not_s % (
                    level,
                    f'valid teritorial ID part (error at \'level\' value space, col {self.value_spaces["level"]!r})'
                )
            )
        other = {}
        if len(teritorial_id) > 1:
            other = super(Nts, self).dispatch_terid(teritorial_id=teritorial_id[1:], errors=errors)

        return {**{'level': level}, **other}


class _NameIDMap(Teryt):
    def __init__(self):
        global nim_initd
        nim_initd = True
        for subsystem in subsystems:
            eval(subsystem)()  # initialize all subsystems classes, they set NIMs
        self.levels = pandas.DataFrame()  # just a placeholder
        self.regions = TF.NtsNIM.search(function='^region', parse=False, by_IDs=True).results
        self.subregions = TF.NtsNIM.search(function='podregion', parse=False, by_IDs=True).results
        self.voivodships = TF.TercNIM.search(function='województwo', parse=False, by_IDs=True).results
        self.powiats = TF.TercNIM.search(function='powiat', parse=False, by_IDs=True).results
        self.gminas = TF.TercNIM.search(function='gmina', parse=False, by_IDs=True).results
        TF.NtsNIM.clear()
        TF.TercNIM.clear()


NameIDMap = Teryt  # (!) shortcut: NIM, real value is an instantiated _NameIDMap class, *assigned externally*
simc = SIMC = Simc
terc = TERC = Terc
nts = NTS = Nts
