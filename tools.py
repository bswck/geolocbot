def are(*args, inside='', exclude=None):
    if exclude is None:
        exclude = []
    args = list(set(args))
    exclude = list(set(([exclude] if isinstance(exclude, str) else exclude)).difference(set(args)))
    if args:
        if exclude:
            for exc_arg in exclude:
                if exc_arg in inside:
                    return False
        for arg in args:
            if arg not in inside:
                return False
    return True


def mass_remove(target: str, *args):
    for arg in args:
        target = str(target).replace(arg, '')
    return target
