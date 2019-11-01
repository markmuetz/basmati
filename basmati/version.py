VERSION = (0, 3, 1, 0, 'alpha')


def get_version(form: str = 'short') -> str:
    """Get BASMATI version

    :param form: one of short, medium or long
    :raises: ValueError if form unrecognized
    :return: basmati version in desired form
    """
    if form == 'short':
        return '.'.join([str(v) for v in VERSION[:3]])
    elif form == 'medium':
        return '.'.join([str(v) for v in VERSION][:4])
    elif form == 'long':
        return '.'.join([str(v) for v in VERSION][:4]) + '-' + VERSION[4]
    else:
        raise ValueError('unrecognized form specifier: {0}'.format(form))


__version__ = get_version()

if __name__ == '__main__':
    print(get_version())
