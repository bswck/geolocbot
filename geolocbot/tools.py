# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import geolocbot
from geolocbot.libs import *

be_quiet = False


def ensure(logical_object, sox: (str, Exception)):
    """ Assert, but raising custom exceptions. """
    dferr = geolocbot.exceptions.GeolocbotError
    if not logical_object:
        raise dferr(sox) | sox
    return True


def no_type_collisions(func_or_meth: typing.Callable):
    ensure(callable(func_or_meth), TypeError('object %r is not callable' % func_or_meth))
    sign = inspect.signature(func_or_meth)
    params = sign.parameters

    def bodyguard(*arguments, **keyword_arguments):
        arg_pos = 0
        args_dict = {}
        hold, key, arg = False, 0, ''

        # zip args with their signatured names
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

        all_args = dict(**args_dict, **keyword_arguments)
        for argument_name, value in params.items():
            if arg_pos < len(all_args):
                argument_annotation = params[argument_name].annotation \
                    if params[argument_name].annotation != params[argument_name].empty else \
                    None
                if argument_annotation is not None:
                    argument = all_args.pop(argument_name, NotImplemented)
                    if argument is NotImplemented:
                        break
                    err = TypeError('%s() got an unexpected type %r of %r parameter (expected type(s): %r)' % (
                        func_or_meth.__name__,
                        type(argument).__name__,
                        argument_name,
                        ', '.join(
                            ['%r' % obj_type.__name__ for obj_type in argument_annotation]
                        ) if isinstance(argument_annotation, typing.Iterable) else type(argument_annotation).__name__
                    ))
                    ensure(isinstance(argument, argument_annotation), err)
                arg_pos += 1

        return func_or_meth(*arguments, **keyword_arguments)

    return bodyguard


def do_nothing(*__args, **__kwargs): pass


class GetLogger(object):
    """ Equivalent for logging.getLogger() made for ``with`` statement syntax. """

    def __init__(self, name='geolocbot'): self.name = name
    def __enter__(self): return geolocbot.libs.logging.getLogger(self.name)
    def __exit__(self, exc_type, exc_val, exc_tb): pass


@no_type_collisions
def representation(cls_name: str, **kwargs):
    kwargs = '(' + ', '.join(['\n    %-13s =    %r' % (k, v) for k, v in kwargs.items()]) + '\n)' if kwargs else ''
    return '%s%s' % (cls_name, kwargs)


@no_type_collisions
def output(*values,
           level: str = 'info',
           sep: str = ' ',
           file: str = 'stdout',
           log: bool = True,
           get_logger: str = 'geolocbot'):
    """ Outputting function. """
    file = getattr(sys, file, sys.stdout)
    values = sep.join([str(values_snippet) for values_snippet in values])
    if log:
        with getLogger(name=get_logger) as handler:
            if isinstance(values, geolocbot.libs.pandas.DataFrame):
                values = values.replace('\n', f'\n{" " * 46}')
            getattr(handler, level, handler.info)(values)
    print(values, file=file) if not be_quiet else do_nothing()
    return values


getLogger = GetLogger


def getter_itself(meth: typing.Callable):
    """ Decorator for getter methods. """
    objn, ni = '_' + meth.__name__, ''
    def wrapper(*args, **__kwargs): return getattr(args[0], objn) if getattr(args[0], objn) is not None else ni
    return wrapper


def deleter(meth: typing.Callable):
    """ Decorator for deleter methods. """
    def wrapper(*args, **__kwargs): setattr(args[0], '_' + meth.__name__, None)
    return wrapper


@no_type_collisions
def tfhook(check: typing.Callable):
    @no_type_collisions
    def inner(callable_: typing.Callable):
        def checker(*_args, **kwargs):
            self, args = (), list(_args)
            if isinstance(args[0], geolocbot.searching.teryt.TerytField):
                self = (args.pop(0),)
            check(*self, _args=args, _kwargs=kwargs)
            return callable_(*_args, **kwargs)

        return checker

    return inner


def _rr_hook(_args, _kwargs):
    exc = _args[0]
    ensure(issubclass(exc, BaseException), 'exceptions must derive from BaseException')


@tfhook(_rr_hook)
@no_type_collisions
def reraise(errtype: type = geolocbot.exceptions.GeolocbotError):
    def wrapper(meth: typing.Callable):
        def sieve(*args, **kwargs):
            try:
                meth(*args, **kwargs)
            except (BaseException, Exception) as _err:
                raise errtype from _err
        return sieve
    return wrapper
