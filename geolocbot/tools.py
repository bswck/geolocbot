# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import geolocbot
from geolocbot.libs import *

be_quiet = False

# colors
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


def ensure(logical_object, xm: (str, Exception)):
    """ Asserts, but raises custom exceptions. """
    dferr = geolocbot.exceptions.BotError
    if not logical_object:
        raise dferr(xm) or xm
    # else:
    return True


def no_type_collisions(callable_: typing.Callable):
    ensure(callable(callable_), TypeError('object %r is not callable' % callable_))
    sign = inspect.signature(callable_)
    params = sign.parameters

    def typechecker(*arguments, **keyword_arguments):
        hold, key, arg_pos, arg, args_dict = False, 0, 0, '', {}

        # 1. Establish arguments' keys.
        for quantum in range(len(arguments)):
            if not hold:
                key = list(params.keys())[quantum]
                arg = params.get(key)
            current_arg = arguments[quantum]
            if '*' in str(arg):
                if key in args_dict:
                    prev = (args_dict[key],) if not isinstance(args_dict[key], tuple) else args_dict[key]
                    args_dict[key] = prev + (current_arg,)
                else:
                    args_dict.update({key: current_arg})
                hold = True
            else:
                args_dict.update({key: current_arg})
                hold = False

        _args = dict(**args_dict, **keyword_arguments)

        # 2. Check if the real types of arguments and keyword arguments passed are matching their annotated types.
        for argument_name, value in params.items():
            if arg_pos < len(_args):
                argument_annotation = params[argument_name].annotation \
                    if params[argument_name].annotation != params[argument_name].empty else \
                    None
                if argument_annotation is not None:
                    argument = _args.pop(argument_name, NotImplemented)
                    if argument is NotImplemented:
                        break
                    argtype_name = type(argument).__name__ if type(argument).__name__ != 'type' else argument
                    err = TypeError(
                        f'{callable_.__name__!s}() got an unexpected type {argtype_name!r} of parameter '
                        f'{argument_name!r} (expected type(s): %s)' % (
                            ', '.join(
                                [f'{obj_type.__name__!r}' for obj_type in argument_annotation]
                            )
                            if isinstance(argument_annotation, typing.Iterable)
                            else type(argument_annotation).__name__
                        ))
                    ensure(isinstance(argument, argument_annotation), err)
                arg_pos += 1

        # 3. All checked: return the called function or method.
        return callable_(*arguments, **keyword_arguments)
    return typechecker


def do_nothing(*__args, **__kwargs): pass


class GetLogger(object):
    """ Equivalent for logging.getLogger() made for ``with`` statement syntax. """
    def __init__(self, name='geolocbot'): self.name = name
    def __enter__(self): return geolocbot.libs.logging.getLogger(self.name)
    def __exit__(self, exc_type, exc_val, exc_tb): pass


@no_type_collisions
def representation(cls_name: str, **kwargs):
    kwargs = '(' + ', '.join(['\n    %-17s =    %r' % (k, v) for k, v in kwargs.items()]) + '\n)' if kwargs else ''
    return f'{cls_name!s}{kwargs!s}'


@no_type_collisions
def output(*values,
           level: str = 'info',
           sep: str = ' ',
           file: str = 'stdout',
           log: bool = True,
           get_logger: str = 'geolocbot'):
    """ Outputting function. """
    # 1. Get the stream file.
    file = getattr(sys, file, sys.stdout)

    # 2. Concatenate the values to an output form.
    values = sep.join([str(values_snippet) for values_snippet in values])

    # 3. Log the values.
    if log:
        with GetLogger(name=get_logger) as handler:
            if isinstance(values, geolocbot.libs.pandas.DataFrame):
                values = values.replace('\n', f'\n{" " * 46}')
            getattr(handler, level, handler.info)(values)

    # 4. Print the values.
    print(values, file=file) if not be_quiet else do_nothing()

    # 5. Return the values.
    return values


def underscored(meth: typing.Callable):
    """ Return value by its name with underscore as first character. """
    methname = '_' + meth.__name__

    def wrapper(cls, *_args, **_kwargs):
        uval = meth(cls) if getattr(cls, methname) is None else getattr(cls, methname)
        return uval

    return wrapper


def underscored_deleter(meth: typing.Callable):
    """ Decorator for deleter methods. """
    def wrapper(*args, **__kwargs): setattr(args[0], '_' + meth.__name__, None)
    return wrapper


def precede_with(hang_on_hook: typing.Callable):
    def wrap(take_off_hook: typing.Callable):
        def hooking(*arguments, **keyword_arguments):
            self, _args, _kwargs = (), list(arguments), keyword_arguments
            if isinstance(_args[0], geolocbot.searching.teryt.TerytField):
                self = (_args.pop(0),)
            hang_on_hook(*self, _args=_args, _kwargs=_kwargs)
            return \
                take_off_hook(*arguments, **keyword_arguments)
        return hooking
    return wrap


# WIP snippet
# -----------
def _rr_hook(_args, _kwargs):
    exc = _args[0]
    ensure(issubclass(exc, BaseException), 'exceptions must derive from BaseException')


@precede_with(_rr_hook)
@no_type_collisions
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
    exec(compile(source='warnings.warn(_warning, category=_category)', filename='Geoloc-Bot', mode='exec', flags=0))
