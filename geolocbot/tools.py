# This is the part of Geoloc-Bot for Nonsensopedia wiki (https://nonsa.pl/wiki/Main_Page).
# Stim, 2020
# GNU GPLv3 license

import geolocbot
from geolocbot.libs import *
from geolocbot.auxiliary_types import TranslatableValue
be_quiet = False


def ensure(condition, m: (str, Exception)):
    """ Assert, but raising custom exceptions. """
    dferr = geolocbot.exceptions.GeolocbotError
    if not condition:
        raise dferr(m) | m
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
                annotated_types = params[argument_name].annotation \
                    if params[argument_name].annotation != params[argument_name].empty else \
                    None
                if annotated_types is not None:
                    argument = all_args.pop(argument_name, NotImplemented)
                    if argument is NotImplemented:
                        break
                    err = TypeError('%s() got an unexpected type %r of %r parameter (expected type(s): %r)' % (
                        func_or_meth.__name__,
                        type(argument).__name__,
                        argument_name,
                        ', '.join(
                            ['%r' % obj_type.__name__ for obj_type in annotated_types]
                        ) if isinstance(annotated_types, typing.Iterable) else type(annotated_types).__name__
                    ))
                    ensure(isinstance(argument, annotated_types), err)
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


@no_type_collisions
def getter(meth: typing.Callable):
    """ Decorator for getter methods. """
    objn, ni = '_' + meth.__name__, TranslatableValue()
    def wrapper(*args, **__kwargs): return getattr(args[0], objn) if getattr(args[0], objn) is not None else ni
    return wrapper


@no_type_collisions
def deleter(meth: typing.Callable):
    """ Decorator for deleter methods. """
    def wrapper(*args, **__kwargs): setattr(args[0], '_' + meth.__name__, None)
    return wrapper
