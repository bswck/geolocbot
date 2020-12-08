# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import geolocbot
from geolocbot.libs import *


class TerminalColors:
    white = u'\u001b[30m'
    red = u'\u001b[31m'
    green = u'\u001b[32m'
    yellow = u'\u001b[33m'
    blue = u'\u001b[34m'
    magenta = u'\u001b[35m'
    cyan = u'\u001b[36m'
    grey = u'\u001b[37m'
    r = u'\u001b[0m'
    b = u'\033[1m'
    br = u'\033[0m'


tc = TerminalColors


def __assert(logical_object, xm: (str, Exception)):
    """ Asserts, but raises custom exceptions. """
    dferr = geolocbot.exceptions.BotError
    if not logical_object:
        raise dferr(xm) or xm
    # else:
    return True


require = __assert


def typecheck(callable_: typing.Callable):
    """
    Decorator for checking if types of passed towards callable arguments are valid (matching callable's annotation).

    Parameters
    ----------
    callable_ : callable
        Function or method to be type-checked.
    """
    __assert(callable(callable_), TypeError('object %r is not callable' % callable_))
    sign = inspect.signature(callable_)
    params = sign.parameters

    def __typecheck(*arguments, **keyword_arguments):
        hold, key, arg_pos, arg, args_dict = False, 0, 0, '', {}

        # 1. Establish args' keys.
        for quantum in range(len(arguments)):
            if not hold:
                key = list(params.keys())[quantum]
                arg = params.get(key)
            current_arg = arguments[quantum]
            if '*' in str(arg):
                if key in args_dict:
                    prev = (args_dict.get(key),) if not isinstance(args_dict[key], tuple) else args_dict[key]
                    args_dict[key] = prev + (current_arg,)
                else:
                    args_dict |= {key: current_arg}
                hold = True
            else:
                args_dict |= {key: current_arg}
                hold = False

        _args = dict(**args_dict, **keyword_arguments)

        # 2. Check if the real types of arguments and keyword arguments passed are matching their annotated types.
        for argument_name, value in params.items():
            if arg_pos < len(_args):
                valid_type = params[argument_name].annotation \
                    if params[argument_name].annotation != params[argument_name].empty else \
                    None
                if valid_type is not None:
                    argument = _args.pop(argument_name, NotImplemented)
                    if argument is NotImplemented:
                        break
                    argtype_name = type(argument).__name__ if type(argument).__name__ != 'type' else argument
                    err = TypeError(
                        f'{callable_.__name__!s}() got an unexpected type {argtype_name!r} of parameter '
                        f'{argument_name!r} (expected type(s): %s)' % (
                            ', '.join(
                                [f'{obj_type.__name__!r}' for obj_type in valid_type]
                            )
                            if isinstance(valid_type, typing.Iterable)
                            else f'{valid_type.__name__!r}'
                        ))
                    __assert(isinstance(argument, valid_type), err)
                arg_pos += 1

        # 3. All checked: return the called function or method.
        return callable_(*arguments, **keyword_arguments)
    return __typecheck


def do_nothing(*__args, **__kwargs): pass


class get_logger(object):
    """ Equivalent for logging.getLogger() made for *with_stmt* syntax. """
    def __init__(self, name='geolocbot'): self.name = name
    def __enter__(self): return logging.getLogger(self.name)
    def __exit__(self, exc_type, exc_val, exc_tb): pass


@typecheck
def representation(cls_name: str, **kwargs):
    max_l = max([len(s) for s in kwargs], default=4)
    indented = f'\n    %-{max_l}s  =  %r'
    kwargs = '(' + ', '.join([indented % (k, v) for k, v in kwargs.items()]) + '\n)' if kwargs else ''
    return f'{cls_name!s}{kwargs!s}'


@typecheck
def output(*values,
           level: str = 'info',
           sep: str = ' ',
           file: str = 'stdout',
           log: bool = True,
           logger: str = 'geolocbot'):
    """ Outputting function. """
    # 1. Get the stream file.
    file = getattr(sys, file, sys.stdout)

    # 2. Concatenate the values to an output form.
    values = sep.join([str(value) for value in values])

    # 3. Log the values.
    if log:
        with get_logger(name=logger) as handler:
            if isinstance(values, geolocbot.libs.pandas.DataFrame):
                values = values.replace('\n', f'\n{" " * 46}')
            getattr(handler, level, handler.info)(values)

    # 4. Write the values in the stream file.
    print(values, file=file)

    # 5. Return the values.
    return values


def setordefault(meth: typing.Callable):
    """ Return set (self._value) or default (returned in the method) value. """
    methname = '_' + meth.__name__
    def wrapper(cls, *_args, **_kwargs): return getattr(cls, methname) if getattr(cls, methname) is not None else meth(
        cls)
    return wrapper


def getpagebyname(callable_: typing.Callable):
    def wrapper(self, pagename: str, *arguments_, **keyword_arguments):
        self.processed_page, arguments = pywikibot.Page(self.site, pagename), (self, pagename, *arguments_)
        return callable_(*arguments, **keyword_arguments)

    return wrapper


def deleter(meth: typing.Callable):
    """ Decorator for deleter methods. """
    def wrapper(*args, **__kwargs): setattr(args[0], '_' + meth.__name__, None)
    return wrapper


def called_after(precedent: typing.Callable):
    def _w(callable_: typing.Callable):
        def _sequence(*arguments, **keyword_arguments):
            self, _args, _kwargs = (), list(arguments), keyword_arguments
            if _args:
                if isinstance(_args[0], geolocbot.searching.teryt.TERYTRegister):
                    self = (_args.pop(0),)
            precedent(*self, _args=_args, _kwargs=_kwargs)
            return \
                callable_(*arguments, **keyword_arguments)
        return _sequence
    return _w


@typecheck
def reverse_(dct: dict):
    return {v: k for k, v in dct.items()}


# noinspection PyArgumentList
@typecheck
def keys_(dct: dict, rtype=tuple, sort: bool = False, key=None):
    if sort:
        return sorted(rtype(dct.keys()), **({'key': key} if key else {}))
    return rtype(dct.keys())


# noinspection PyArgumentList
@typecheck
def values_(dct: dict, rtype=tuple, sort: bool = False, key=None):
    if sort:
        return sorted(rtype(dct.values()), **({'key': key} if key else {}))
    return rtype(dct.values())


def lcx(x: typing.Any, seq: typing.Iterable, _lcx=True):
    """
    Check if *x* is (or is not) in each sequence element.

    Parameters
    ----------
    x : any
        Value to compare with each *seq* element.
    seq : iterable
        Iterable containing values comparable with *x*.
    _lcx : bool
        Whether to check if each *seq* element contains *x* or it does not.

    Returns
    -------
    list
        List with boolean values only.

    """
    return [x in elem for elem in seq] if _lcx else [x not in elem for elem in seq]


def xcl(seq: typing.Iterable, x: typing.Any, _xcl=True):
    """
    Check if each sequence element is (or is not) in x.

    Parameters
    ----------
    seq : iterable
        Iterable containing values comparable with *x*.
    x : any
        Value to compare with each *seq* element.
    _xcl : bool
        Whether to check if *x* contains each *seq* element or it does not.

    Returns
    -------
    list
        List with boolean values only.

    """
    return [elem in x for elem in seq] if _xcl else [elem not in x for elem in seq]


# WIP snippet
# -----------
def __reraise(_args, _kwargs):
    exc = _args[0]
    __assert(issubclass(exc, BaseException), 'exceptions must derive from BaseException')


@called_after(__reraise)
@typecheck
def reraise(errtype: type = geolocbot.exceptions.BotError):
    def wrapper(callable_: typing.Callable):
        def sieve(*arguments, **keyword_arguments):
            try:
                callable_(*arguments, **keyword_arguments)
            except (BaseException, Exception) as _err:
                raise errtype from _err
        return sieve
    return wrapper
# -----------


def anonymous_warning(_warning, _category=FutureWarning):
    exec(compile(source='warnings.warn(_warning, category=_category)', filename='bot', mode='exec', flags=0))


def notna(value) -> "bool":
    return value != 'nan' and value is not nan
