# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

from .utils import *
from .libs import *
from .prepare import *
sys.path.extend(str(pathlib.Path(os.getcwd()).parent))

subsystems = ('simc', 'terc', 'nts')
_NIM_initialized = False
__all__ = ('transferred_searches', *subsystems)


def load_nim():
    global NameIDMaps
    NameIDMaps = GetNIMs()
    return True


class _TERYTAssociated:
    """ TERYT-associated object marker. """
    def __repr__(self): return representation(type(self).__name__, **dict(self))

    def __iter__(self):
        for attrname in [attr for attr in keys_(self.__dict__) if attr[:1] != '_']:
            yield attrname, getattr(self, attrname)


class __CTRP(_TERYTAssociated):
    """ Common TERYTRegister properties. """
    def __init__(self):
        self.gmitype_nim = {
            'miejska': '1',
            'gmina miejska': '1',
            'wiejska': '2',
            'gmina wiejska': '2',
            'miejsko-wiejska': '3',
            'gmina miejsko-wiejska': '3',
            'miasto w gminie miejsko-wiejskiej': '4',
            'obszar wiejski w gminie miejsko-wiejskiej': '5',
            'dzielnice m. st. Warszawy': '8',
            'dzielnice Warszawy': '8',
            'dzielnica Warszawy': '8',
            'dzielnica': '8',
            'delegatury w miastach: Kraków, Łódź, Poznań i Wrocław': '9',
            'delegatura': '9'
        }

    @property
    @setordefault
    def terid(self):
        """ Teritorial ID of a locality. Common for all locally-defined subsystems. """
        return ''

    @terid.deleter
    @deleter
    def terid(self):
        return

    @property
    @setordefault
    def level(self):
        """ Level of a locality. Occurs in NTS subsystem only. """
        return ''

    @level.deleter
    @deleter
    def level(self):
        return

    @property
    @setordefault
    def region(self):
        """ Region of a locality. Occurs in NTS subsystem only. """
        return ''

    @region.deleter
    @deleter
    def region(self):
        return

    @property
    @setordefault
    def subregion(self):
        """ Subregion of a locality. Occurs in NTS subsystem only. """
        return ''

    @subregion.deleter
    @deleter
    def subregion(self):
        return

    @property
    @setordefault
    def voivodship(self):
        """ Voivodship of a locality. Common for all locally-defined subsystems. """
        return ''

    @voivodship.deleter
    @deleter
    def voivodship(self):
        return

    @property
    @setordefault
    def powiat(self):
        """ Powiat of a locality. Common for all locally-defined subsystems. """
        return ''

    @powiat.deleter
    @deleter
    def powiat(self):
        return

    @property
    @setordefault
    def gmina(self):
        """ Gmina of a locality. Common for all locally-defined subsystems. """
        return ''

    @gmina.deleter
    @deleter
    def gmina(self):
        return

    @property
    @setordefault
    def gmitype(self):
        """ Type of the gmina of a locality. Common for all locally-defined subsystems. """
        return ''

    @gmitype.deleter
    @deleter
    def gmitype(self):
        return

    @property
    @setordefault
    def loctype(self):
        """ Locality type. Occurs in SIMC subsystem only. """
        return ''

    @loctype.deleter
    @deleter
    def loctype(self):
        return

    @property
    @setordefault
    def has_common_name(self):
        """ Whether a locality has its common name. Occurs in SIMC subsystem only. """
        return ''

    @has_common_name.deleter
    @deleter
    def has_common_name(self):
        return

    @property
    @setordefault
    def name(self):
        """ Name of a locality. Common for all locally-defined subsystems. """
        return ''

    @name.deleter
    @deleter
    def name(self):
        return

    @property
    @setordefault
    def function(self):
        """ Function of a locality. Common for TERC and NTS subsystems. """
        return ''

    @function.deleter
    @deleter
    def function(self):
        return

    @property
    @setordefault
    def id(self):
        """ ID (not teritorial!) of a locality. Occurs in SIMC subsystem only. """
        return ''

    @id.deleter
    @deleter
    def id(self):
        return

    @property
    @setordefault
    def integral_id(self):
        """ ID (not teritorial!) of an integral locality of a locality. Occurs in SIMC subsystem only. """
        return ''

    @integral_id.deleter
    @deleter
    def integral_id(self):
        return

    @property
    @setordefault
    def date(self):
        """ State of this date. Common for all locally-defined subsystems. """
        return ''

    @date.deleter
    @deleter
    def date(self):
        return

    @property
    @setordefault
    def entry_frame(self):
        """ Single entry frame. """
        return pandas.DataFrame()

    @entry_frame.deleter
    @deleter
    def entry_frame(self):
        return

    @property
    @setordefault
    def results(self):
        """ Results of self.search(). """
        return pandas.DataFrame()

    @results.deleter
    @deleter
    def results(self):
        return


class _BoundNameAndID(_TERYTAssociated):
    """ Twofold object containing TERYT ID and name linked to that ID. """
    @typecheck
    def __init__(self, name: (str, bool) = '', identificator: str = ''):
        self.name = self.Name = name
        self.id = self.ID = self.Id = identificator
        self.items_t = values_(dict(self))

    @typecheck
    def __getitem__(self, item: (int, str)):
        return self.items_t[item] if isinstance(item, int) else getattr(self, item, '')

    def __repr__(self):
        return '(' + ', '.join([repr(value) for value in values_(dict(self))]) + ')'

    def __str__(self):
        return str(self.id) if self.id else ''

    def __add__(self, other):
        return (str(self.id) + other) if self else ('' + other)

    def __bool__(self):
        return all([self.name, notna(str(self.id))])

    def __iter__(self):
        if self.name:
            yield 'name', self.name
        yield 'ID', self.id


_tsearches = {}


def transferred_searches(name):
    for transfer in tuple(set(_tsearches.get(name, ()))):
        yield getattr(transfer, '_field_name'), transfer


class _Loc(_TERYTAssociated):
    """ Broker for DataFrame indexing with LocationIndexer. """
    def approve_col(self=_TERYTAssociated):
        def decorator(meth: typing.Callable):
            def wrapper(*args, **kwargs):
                __self, col, df = self, kwargs['col'], kwargs['df']
                if isinstance(col, str):
                    require(col in df.columns, f'no column named {col!r}')
                    kwargs['col'] = df[col]
                return meth(*args, **kwargs)
            return wrapper
        return decorator

    approve_col = approve_col()

    @staticmethod
    @approve_col
    @typecheck
    def name(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col == value) \
            if case else \
            (col.str.lower() == value.lower())
        return df.loc[query]

    equal = name

    @staticmethod
    @approve_col
    @typecheck
    def match(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.match(value, case=case))
        return df.loc[query]

    @staticmethod
    @approve_col
    @typecheck
    def contains(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.contains(value, case=case, na=False))
        return df.loc[query]

    @staticmethod
    @approve_col
    @typecheck
    def startswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.startswith(value, na=False)) \
            if case else \
            (col.str.lower().str.startswith(value.lower()))
        return df.loc[query]

    @staticmethod
    @approve_col
    @typecheck
    def endswith(*, df: pandas.DataFrame, col: (pandas.Series, str), value: str, case: bool):
        query = \
            (col.str.endswith(value, na=False)) \
            if case else \
            (col.str.lower().str.endswith(value.lower(), na=False))
        return df.loc[query]


class _Search(_TERYTAssociated):
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
        """ Internal method marking if no search were found. """
        return self.candidate.empty or self.candidate.equals(self.dataframe)

    def shuffle(self):
        """
        Shuffle search indicators for searching.

        Returns
        -------
        dict
            Shuffled search indicators.
        """
        keys, values = keys_(self.search_indicators, rtype=list), values_(self.search_indicators, rtype=list)
        inef_key_index = keys.index(self.ineffective_value_space)
        inef_value = values[inef_key_index]
        del keys[inef_key_index], values[inef_key_index]
        keys.insert(inef_key_index + 1, self.ineffective_value_space)
        values.insert(inef_key_index + 1, inef_value)
        self.search_indicators = dict(zip(keys, values))
        return self.search_indicators

    def _search(self, search_indicators):
        self.candidate = self.dataframe.copy()
        self.search_indicators = search_indicators
        value_spaces = self.value_spaces
        self.frames = [self.candidate]

        def initial_search():
            self.candidate = getattr(_Loc, self.search_mode)(
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
                if value_space not in self.value_spaces:
                    continue
                col = self.value_spaces[value_space]
                stuff = dict(df=self.candidate, col=col, value=str(query), case=self.case)
                self.candidate = \
                    _Loc.contains(**stuff) if value_space in self.container_values else \
                    _Loc.startswith(**stuff) if value_space in self.startswith_values else \
                    _Loc.name(**stuff)

                if self.failure():
                    if self.candidate.equals(self.dataframe):
                        warn(f'It seems that all values in {value_space!r} value space are equal to '
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


class TERYTRegister(ABC, __CTRP, metaclass=bABCMeta):
    """
    TERYT register, _Search broker.
    If self.search() is allowed to parse, this class contains single TERYT entry properties defined in _CTP after
    getting 1 result from self.search().
    """
    TERCNIM = None  # parallel object binding identifiers to linked to them names in the background
    NTSNIM = None  # parallel object binding identifiers to linked to them names in the background

    def __init__(
            self,
            *,
            field_name: str,
            sub,
            simc_resource=resources.cached_teryt.simc,
            terc_resource=resources.cached_teryt.terc,
            nts_resource=resources.cached_teryt.nts
    ):
        super(TERYTRegister, self).__init__()
        if not _NIM_initialized:
            load_nim()
        self._invalid_kwd_msg = \
            f'%s() got an unexpected keyword argument %r. Try looking for the proper argument name ' \
            f'in the following list:\n{" " * 12}%s.'
        self._repr_not_str = '%r is not a %s'
        self.simc, self.terc, self.nts = simc_resource, terc_resource, nts_resource
        self._field_name = field_name.replace(' ', '_').upper()
        self.field: pandas.DataFrame = getattr(self, self._field_name.lower(), None)
        require(self.field is not None, f'couldn\'t fetch searching.teryt.{self._field_name.lower()}')
        require(not self.field.empty, 'cannot instantiate _TFSearch with an empty field')
        self._candidate = None  # auxiliary
        self._container_values = ('function',)  # auxiliary
        self._name_value_space_kwds = ('name', 'match', 'startswith', 'endswith', 'contains')  # auxiliary
        self._bool_optional = ('veinf', 'force_dispatch', 'dispatch', 'parse', 'by_IDs', 'match_case')  # auxiliary
        self._str_optional = ('terid',)  # auxiliary
        self._other_kwds = self._bool_optional + self._str_optional  # auxiliary
        self._derr = geolocbot.exceptions.DispatcherError  # auxiliary
        self._startswith_values = ('date',)  # auxiliary
        self.case = None
        self.cols, self.len = [col for col in self.field.columns], len(self.field)
        self.columns = self.cols
        self.conflicts = (self._name_value_space_kwds, ('force_dispatch', 'dispatch'))
        self.fdispatch, self._valid_kwds, self.name_value_space, self.dispatch = None, None, None, None
        self.search_indicators, self._search_only_kwds, self.search_mode, self.veinf = None, None, None, None
        self.parse = None
        self.results_found = False
        self.dispatched = False
        self.parsed = False
        self._argid = {}  # auxiliary
        self._argshed = {}  # auxiliary
        self._sfo: TERYTRegister = sub  # subclass field object
        self._transfer_target = None  # subclass field object used for getting search indicators from local properties
        self._cached_nims = {}

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
        self._gmitype = None  # (!) real value is assigned by parser(s)
        self._loctype = None  # (!) real value is assigned by parser(s)
        self._has_common_name = None  # (!) real value is assigned by parser(s)
        self._name = None  # (!) real value is assigned by parser(s)
        self._date = None  # (!) real value is assigned by parser(s)
        self._entry_frame = None  # (!) real value is assigned by parser(s)
        self._results = None  # (!) real value is assigned by parser(s)
        # End of single entry values

    def __repr__(self):
        fn = self._field_name.upper()
        return representation(
            fn if not self.dispatched and not self.results_found
            else fn + '\n(*.results – accessor for results in a DataFrame)'
            if self.results_found and not self.dispatched else fn + 'Entry', **dict(self)
        )

    def __iter__(self):
        if getattr(self, 'terid'):
            yield 'terid', getattr(self, 'terid')
        for value_space in self.value_spaces:
            if getattr(self, value_space):
                yield value_space, getattr(self, value_space)

    def __getitem__(self, item):
        return dict(self)[item]

    def __del__(self):
        self.__init__(
            **{self._field_name.lower() + '_resource': self.field},
            field_name=self._field_name,
            sub=self
        )

    clear = __del__

    @abstractattribute
    def value_spaces(self):
        return {}

    @abstractattribute
    def nim_value_spaces(self):
        return {}

    @typecheck
    def _has_dict_nim(self, value_space: str) -> "bool":
        """ Check if *self* has dict-type attribute standing for value space's NIM. """
        return hasattr(self, value_space + '_nim')

    @typecheck
    def _has_df_nim(self, value_space: str) -> "bool":
        """ Check if *self* has DataFrame-type attribute standing for value space's NIM. """
        return hasattr(NameIDMaps, value_space + 's')

    @typecheck
    def _has_nim(self, value_space: str) -> "bool":
        """ Check if *value_space* has NIM. """
        return self._has_dict_nim(value_space) or self._has_df_nim(value_space)

    # ---- Preceding methods
    def __generate_indicators(self, _args, _kwargs):
        """ Precede self.generate_indicators(). """
        require(_args, 'generate_indicators(): no arguments')
        target_name = _args[0]
        require(target_name in subsystems, f'cannot evalue transfer target using name {target_name!r}')
        self._transfer_target = \
            eval(f'{target_name!s}')
        self._transfer_target = self._transfer_target()
        require(
            self.dispatched,
            'cannot perform generating indicators from properties if search results were not parsed'
        )

    def __get_ids_by_names(self, _args, _kwargs):
        """ Precede self._get_ids_by_names(). """
        valid_kwds = keys_(self.value_spaces, sort=True)
        # 1. Check if all keyword arguments are expected
        [require(
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
                require(value in nim, self._repr_not_str % (value, f'valid \'{name.replace("_", " ")}\' non-ID value'))
                value = nim[value]
            self._argshed |= {name: value}  # don't lose the other arguments

    def __get_name_by_id(self, _args, _kwargs):
        """ Precede self._get_name_by_id(). """
        if _args:
            value_space = _args[0]
            require(self._has_nim(value_space), f'value space {value_space!r} does not have a name-ID map')

    def __dispatch_entry(self, _args, _kwargs):
        """ Precede self.dispatch_entry(). """
        dataframe, value_spaces = _kwargs.pop('dataframe', self.results), self.value_spaces
        require(not dataframe.empty, self._derr('dispatcher failed: nothing to dispatch from'))
        require(
            len(dataframe) == 1,
            self._derr(
                f'dispatcher failed: cannot dispatch from more than one TERYT entry (got {len(dataframe)} entries)'
            )
        )
        for value_space in value_spaces:
            require(
                value_spaces[value_space] in dataframe,
                self._derr(
                    f'dispatcher failed: value space {value_space.replace("_", " ")} '
                    f'(the real column is named {value_spaces[value_space]!r}) not in source DataFrame'
                )
            )
        self._entry_frame = dataframe

    def __search(self, _args, _kwargs):
        """ Precede self.search(). """
        self.clear()
        keywords = _kwargs

        # 1. Check common conditions
        require(
            not _args,
            ValueError(
                'cannot perform searching: please specify the arguments with their keys in the \'key=value\' '
                'form, e.g.: search(startswith=\'a\')')
        )
        require(keywords, ValueError('cannot perform searching: no keyword arguments'))

        # 2. Check if arguments and their types are expected
        self._search_only_kwds = tuple(
            set(self._name_value_space_kwds + keys_(self.value_spaces))
        ) + self._str_optional
        self._valid_kwds = self._search_only_kwds + self._other_kwds
        for keyword, value in keywords.items():
            require(
                keyword in self._valid_kwds,
                ValueError(self._invalid_kwd_msg % (
                    'search', keyword, ', '.join(sorted(set(self._valid_kwds)))
                ))
            )
            valid_type = (bool,) if keyword in self._bool_optional or keyword.startswith('has') \
                else (str, _BoundNameAndID)
            str_valid_types = (', '.join([repr(_type.__name__) for _type in valid_type])
                               if isinstance(valid_type, typing.Iterable) else type(valid_type).__name__)
            invalid_type_msg = f'search() got an unexpected type {type(value).__name__!r} of parameter ' \
                               f'{keyword!r} (expected type(s): %s)' % str_valid_types
            if isinstance(value, _BoundNameAndID):
                keywords[keyword] = value.id
            require(isinstance(value, valid_type), TypeError(invalid_type_msg))

        # 3. Check if any search keyword argument has been provided
        require(any(xcl(x=keywords, seq=self._search_only_kwds)), ValueError(
                f'no keyword arguments for searching (expected minimally 1 from: '
                f'{", ".join(sorted(self._search_only_kwds))})')
                )

        self.conflicts += tuple(('terid', nim_value_space) for nim_value_space in self.nim_value_spaces)

        # 4. Handle conflicts
        for conflicted in self.conflicts:
            conflict = []
            for argument in conflicted:
                if argument in keywords:
                    require(
                        not conflict,
                        'setting more than one keyword argument from %s in one search is impossible' %
                        ' and '.join([f'\'{conflicted_arg!s}=…\'' for conflicted_arg in sorted(conflicted)])
                    )
                    conflict.append(argument)

        self.name_value_space, self.fdispatch = None, True
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
        self.dispatch = keywords.pop('dispatch', True)
        self.parse = keywords.pop('parse', True)
        self.fdispatch, self.case = keywords.pop('force_dispatch', False), keywords.pop('match_case', False)
        self.by_IDs = keywords.pop('by_IDs', False)
        terid = keywords.pop('terid', '')

        # 7. Set the search indicators
        if not self.by_IDs:
            keywords = self._get_ids_by_names(**keywords)
        if terid:
            parsed_terid = self.parse_terid(terid)
            [keywords.__setitem__(n, v) for n, v in parsed_terid.items() if v]

        self.search_indicators = keywords
        self._candidate, frames = self.field.copy(), [self.field.copy()]

        for value_space in self.search_indicators:
            column = self.value_spaces[value_space]
            self.field[column] = self.field[self.value_spaces[value_space]].map(str)  # map all to strings

        return True

    # ----------

    @called_after(__get_ids_by_names)
    def _get_ids_by_names(self, **_kwargs):
        id_indicators = self._argshed.copy()
        for value_space in keys_(self._argshed):
            if value_space not in self.TERCNIM.columns:
                id_indicators.pop(value_space)

        spaces = keys_(self.value_spaces)
        for value_space, value in self._argid.items():
            pvalue_space = value_space + 's'
            id_dataframe = getattr(NameIDMaps, pvalue_space)

            if id_dataframe.empty:
                warn(
                    f'no name-ID map available for {pvalue_space}. Updating search indicators with the provided value, '
                    f'however results are possible not to be found if it is not a valid ID.'
                )
                id_indicators |= {value_space: value}
                continue

            entry = _Search(
                dataframe=id_dataframe,
                field_name=getattr(self.TERCNIM, '_field_name'),
                search_mode='equal',
                value_spaces=self.value_spaces,
                case=False,
                container_values=self._container_values,
                startswith_values=self._startswith_values,
                name_space_value=value
            )(search_indicators=id_indicators)

            require(not entry.empty, self._repr_not_str % (value, value_space))
            id_indicators |= {value_space: entry.iat[0, entry.columns.get_loc(self.value_spaces[value_space])]}

            if value_space != spaces[0]:
                quantum = spaces.index(value_space) - 1
                for rot in range(quantum + 1):
                    prev = spaces[quantum - rot]
                    id_indicators[prev] = entry.iat[0, entry.columns.get_loc(self.value_spaces[prev])]

        return {**id_indicators, **self._argshed}

    def __handle_results(self):
        """ Handle results. """
        if self._failure():
            def _hf():
                """ Handle failure. """
                self.__del__()
                require(not self.veinf, ValueError('no results found'))
                return self._sfo
            return _hf()
        else:
            self.results_found = True
            self._results = self._candidate.reset_index()
            if (len(self._candidate) == 1 or self.fdispatch) and self.dispatch:
                self.dispatch_entry()
            return self._sfo

    @called_after(__get_name_by_id)
    @typecheck
    def _get_name_by_id(self, value_space: str, value: str):
        if self._has_dict_nim(value_space):
            return reverse_(getattr(self, value_space + '_nim'))[value]

        tfnim = self.TERCNIM \
            if value_space in self.TERCNIM.value_spaces \
            else self.NTSNIM \
            if value_space in self.NTSNIM.value_spaces \
            else do_nothing()

        if any([tfnim is None, value_space not in self.nim_value_spaces, value is nan]):
            return ''

        indicators = {'function': self.value_spaces[value_space]}  # e.g. 'woj' will match 'województwo' etc.
        spaces = keys_(self.value_spaces, rtype=list)

        if value_space != spaces[0]:
            quantum = spaces.index(value_space) - 1
            for rot in range(quantum + 1):
                prev = spaces[quantum - rot]
                indicators[prev] = str(getattr(self, '_' + prev))

        indicators[value_space] = value

        if value_space != spaces[-1]:
            next_ = spaces[spaces.index(value_space) + 1]
            indicators[next_] = 'nan'

        if tuple(indicators.items()) in self._cached_nims:
            return self._cached_nims[tuple(indicators.items())]

        nim_df = _Search(
            dataframe=tfnim.field,
            field_name=getattr(tfnim, '_field_name'),
            search_mode='no_name_col',
            value_spaces=tfnim.value_spaces,
            case=False,
            container_values=getattr(tfnim, '_container_values'),
            startswith_values=getattr(tfnim, '_startswith_values'),
        )(search_indicators=indicators)

        ni = nim_df.iat[0, nim_df.columns.get_loc(tfnim.value_spaces['name'])]
        self._cached_nims |= {tuple(indicators.items()): ni}
        return ni

    def _failure(self):
        """ Internal method, returns True if there were no search results. """
        return self._candidate.empty or self._candidate.equals(self.field)

    @called_after(__generate_indicators)
    @typecheck
    def _generate_indicators(self, _transfer_target_name: str):
        transfer_target = self._transfer_target
        properties = dict(self)
        name_space_value = properties.pop('name')
        prop_copy = properties.copy()
        [
            properties.__setitem__(k, str(v))
            if k in transfer_target.value_spaces and str(v)
            else properties.__delitem__(k)
            for k, v in prop_copy.items()
        ]
        indicators = {**properties, 'by_IDs': True, 'name': name_space_value, 'veinf': self.veinf,
                      'force_dispatch': self.fdispatch, 'match_case': self.case}
        yield indicators
        yield transfer_target

    def set_terid(self) -> "TERYTRegister":
        """
        Set the teritorial ID of a locality.

        Returns
        -------
        TERYTRegister
            self
        """
        self._terid = ''.join(
            [str(getattr(self, tid)) for tid in self.nim_value_spaces if notna(str(getattr(self, tid)))]
        )
        return self

    @typecheck
    def parse_terid(self, teritorial_id: str, errors: bool = True):
        """
        Parse a teritorial ID.

        Examples
        --------
        >>> my_search = SIMC()
        >>> my_search.parse_terid('241003')
        {'voivodship': '24', 'powiat': '10', 'gmina': '03'}

        >>> my_search.parse_terid('249903')
        geolocbot.exceptions.BotError: parse_terid(…, errors=True, …):
            '…99' is not a valid teritorial ID part (error at 'powiat' value space, col 'POW')

        >>> my_search.parse_terid('249903', errors=False)
        {'voivodship': '24', 'powiat': '99', 'gmina': '03'}


        Parameters
        ----------
        teritorial_id
            Teritorial ID to be parsed.
        errors
            Whether to check if the given ID exists in the subsystem's database. Defaults to True.

        Returns
        -------
        dict
            Dictionary containing value spaces and ID parts linked to them.
        """
        require(teritorial_id, 'teritorial ID to be parsed cannot be an empty string')
        code_indicators = {}
        frames = {}
        max_len = sum(values_(self.nim_value_spaces))
        require(
            len(teritorial_id) <= max_len,
            f'{self._field_name.upper()} teritorial ID length is expected to be maximally {max_len}'
        )
        index = 0

        for dfnim_value_space, valid_length in self.nim_value_spaces.items():
            if index >= len(teritorial_id) - 1:
                break
            frames |= {dfnim_value_space: getattr(NameIDMaps, dfnim_value_space + 's')}
            partial = teritorial_id[index:index + valid_length]
            dispatch = self.dispatch
            if errors:
                require(
                    not self.search(by_IDs=True, dispatch=False, **{dfnim_value_space: partial}).results.empty,
                    'parse_terid(…, errors=True, …): ' + self._repr_not_str % (
                        '…' + partial,
                        f'valid teritorial ID part '
                        f'(error at {dfnim_value_space!r} value space, col {self.value_spaces[dfnim_value_space]!r})'
                    )
                )
            self.dispatch = dispatch
            code_indicators |= {dfnim_value_space: partial}
            index += valid_length

        return code_indicators

    @called_after(__dispatch_entry)
    @typecheck
    def dispatch_entry(self, *, _dataframe: pandas.DataFrame = None):
        """
        Dispatch TERYT entry values to local properties.

        Parameters
        ----------
        _dataframe
            Source of the data to be parsed.

        Returns
        -------
        TERYTRegister
            self
        """
        for value_space, colname in self.value_spaces.items():
            value = self._entry_frame.iat[0, self._entry_frame.columns.get_loc(colname)]
            if notna(value):
                setattr(
                    self, '_' + value_space,
                    _BoundNameAndID(identificator=value, name=self._get_name_by_id(value_space, value))
                    if self._has_nim(value_space) and self.parse
                    else value
                )
        self.set_terid()
        self.dispatched = True
        return self._sfo

    @called_after(__search)
    def search(self, *_args, **_kwargs) -> "TERYTRegister":
        """
        Search TERYT subsystem.

        Examples
        --------
        >>> my_search = SIMC()  # instantiate the subsystem
        >>> my_search.search(name='Poznań')
        SIMC
        (*.results – accessor for results in a DataFrame)

        >>> my_search.results  # search results
           index WOJ POW GMI RODZ_GMI  RM MZ   NAZWA      SYM   SYMPOD     STAN_NA
        0  10815  06  11  06        2  01  1  Poznań  0686397  0686397  2020-01-01
        1  75791  24  10  03        2  00  1  Poznań  0217047  0216993  2020-01-01
        2  95742  30  64  01        1  96  1  Poznań  0969400  0969400  2020-01-01

        >>> my_search.search(name='Poznań', voivodship='śląskie')  # 1 entry, properties (e.g. self.terid) are available
        SIMCEntry(
            terid            =  '2410032',
            voivodship       =  ('ŚLĄSKIE', '24'),
            powiat           =  ('pszczyński', '10'),
            gmina            =  ('Miedźna', '03'),
            gmitype          =  ('gmina wiejska', '2'),
            loctype          =  ('część miejscowości', '00'),
            has_common_name  =  (True, '1'),
            name             =  'Poznań',
            id               =  '0217047',
            integral_id      =  '0216993',
            date             =  '2020-01-01'
        )

        Returns
        -------
        self
        """
        self._candidate = _Search(
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

    @typecheck
    def to_list(self, value_space: str, usenim: bool = True) -> "list":
        """
        Get list of all values in a given value space.

        Parameters
        ----------
        value_space : str
            Name of the target value space.
        usenim : bool
            Whether to return name-ID map extracts (see: _BoundNameAndID); defaults to True.

        Returns
        -------
        list
        """
        dataframe = self.field.copy() if not self.results_found else self.results.copy()
        require(
            value_space in self.value_spaces,
            f'{value_space!r} is not a valid value space name. Available value spaces: '
            f'{", ".join(keys_(self.value_spaces, sort=True))}'
        )
        lst = getattr(dataframe, self.value_spaces[value_space]).tolist()
        if usenim and self._has_nim(value_space):
            for key_index in range(len(lst)):
                self.dispatch_entry(dataframe=pandas.DataFrame([dataframe.loc[dataframe.index[key_index]]]))
                # TODO: cleaning after parsing (which is in fact auxiliary)
                lst[key_index] = _BoundNameAndID(
                    identificator=lst[key_index],
                    name=self._get_name_by_id(value_space=value_space, value=lst[key_index])
                )
        return lst

    @typecheck
    def to_dict(self, usenim: bool = True) -> "dict":
        """
        Convert field (see: self.field) part to dict.

        Parameters
        ----------
        usenim : bool
            Whether to return name-ID map extracts (see: _BoundNameAndID); defaults to True.

        Returns
        -------
        dict
        """
        results = self.results.copy()  # don't lose the current results
        dictionary = {}
        for value_space in self.value_spaces:
            value = tuple(self.to_list(value_space, usenim=usenim))
            dictionary |= {value_space: value[0] if len(value) == 1 else value}
        self.clear()
        self._results = results
        return dictionary

    @typecheck
    def transfer(self, transfer_target_name: str, **other) -> "TERYTRegister":
        """
        Search another TERYT subsystem using currently available properties (e.g. self.name, self.voivodship).

        Parameters
        ----------
        transfer_target_name : str
            Name of the subsystem, e.g. 'SIMC'.
        """
        indicators, transfer_target = self._generate_indicators(transfer_target_name)
        global _tsearches
        name = indicators['name']
        _tsearches[name] = _tsearches.pop(name, ()) + (self, transfer_target.search(
            **{vs: v for vs, v in other.items() if vs in transfer_target.value_spaces},
            **indicators)
        )
        return _tsearches[name][-1]


class SIMC(TERYTRegister):
    """ SIMC, TERYT subsystem. """
    def __init__(self, resource=resources.cached_teryt.simc, *_args, **_kwargs):
        super(SIMC, self).__init__(field_name='simc', sub=self, simc_resource=resource)
        self.value_spaces = {
            'voivodship': 'WOJ', 'powiat': 'POW', 'gmina': 'GMI', 'gmitype': 'RODZ_GMI', 'loctype': 'RM',
            'has_common_name': 'MZ', 'name': 'NAZWA', 'id': 'SYM', 'integral_id': 'SYMPOD', 'date': 'STAN_NA'
        }
        # ↑ See: https://bit.ly/2VqfxMG ('SIMC' tab)
        self.has_common_name_nim = {True: '1', False: '0'}
        self.nim_value_spaces = {'voivodship': 2, 'powiat': 2, 'gmina': 2, 'gmitype': 1}
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


class TERC(TERYTRegister):
    """ TERC, TERYT subsystem. """
    def __init__(self, resource=resources.cached_teryt.terc, *_args, **_kwargs):
        super(TERC, self).__init__(field_name='terc', sub=self, terc_resource=resource)
        TERYTRegister.TERCNIM = self
        self.value_spaces = {
            'voivodship': 'WOJ', 'powiat': 'POW', 'gmina': 'GMI', 'gmitype': 'RODZ', 'name': 'NAZWA',
            'function': 'NAZWA_DOD', 'date': 'STAN_NA',
        }
        self.nim_value_spaces = {'voivodship': 2, 'powiat': 2, 'gmina': 2, 'gmitype': 1}


class NTS(TERYTRegister):
    """ NTS, TERYT subsystem. """
    # TODO: check for NIM of levels
    def __init__(self, resource=resources.cached_teryt.nts, *_args, **_kwargs):
        super(NTS, self).__init__(field_name='nts', sub=self, nts_resource=resource)
        TERYTRegister.NTSNIM = self
        self.value_spaces = {
            'level': 'POZIOM', 'region': 'REGION', 'voivodship': 'WOJ', 'subregion': 'PODREG', 'powiat': 'POW',
            'gmina': 'GMI', 'gmitype': 'RODZ', 'name': 'NAZWA', 'function': 'NAZWA_DOD', 'date': 'STAN_NA'
        }
        self.nim_value_spaces = {
            'region': 1, 'voivodship': 2, 'subregion': 2, 'powiat': 2, 'gmina': 2, 'gmitype': 1
        }

    @typecheck
    def parse_terid(self, teritorial_id: str, errors: bool = True):
        require(teritorial_id, 'teritorial ID to be parsed cannot be an empty string')
        level = teritorial_id[0]
        if errors:
            require(
                not self.search(by_IDs=True, dispatch=False, **{'level': level}).results.empty,
                'dispatch_terid(…, errors=True, …): ' + self._repr_not_str % (
                    level,
                    f'valid teritorial ID part (error at \'level\' value space, col {self.value_spaces["level"]!r})'
                )
            )
        other = {}
        if len(teritorial_id) > 1:
            other = super(NTS, self).parse_terid(teritorial_id=teritorial_id[1:], errors=errors)

        return {**{'level': level}, **other}


class GetNIMs(_TERYTAssociated):
    """ Get Name-ID maps. """
    def __init__(self):
        global _NIM_initialized
        _NIM_initialized = True
        for subsystem in subsystems:
            eval(subsystem)()  # initialize all subsystems classes to set NIMs
        self.levels = pandas.DataFrame()  # just a placeholder
        self.regions = TERYTRegister.NTSNIM.search(function='^region', dispatch=False, by_IDs=True).results
        self.subregions = TERYTRegister.NTSNIM.search(function='podregion', dispatch=False, by_IDs=True).results
        self.voivodships = TERYTRegister.TERCNIM.search(function='województwo', dispatch=False, by_IDs=True).results
        self.powiats = TERYTRegister.TERCNIM.search(function='powiat', dispatch=False, by_IDs=True).results
        self.gminas = TERYTRegister.TERCNIM.search(function='gmina', dispatch=False, by_IDs=True).results
        TERYTRegister.NTSNIM.clear()
        TERYTRegister.TERCNIM.clear()


NameIDMaps = _TERYTAssociated  # (!) shortcut: NIM, real value is an instantiated GetNIM class
simc = Simc = SIMC
terc = Terc = TERC
nts = Nts = NTS

del ABC, bABCMeta  # not for export
