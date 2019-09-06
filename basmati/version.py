VERSION = (0, 1, 0, 0, 'alpha')


def get_version(version=VERSION, form='short'):
    if form == 'short':
        return '.'.join([str(v) for v in version[:3]])
    elif form == 'medium':
        return '.'.join([str(v) for v in version][:4])
    elif form == 'long':
        return '.'.join([str(v) for v in version][:4]) + '-' + version[4]
    else:
        raise ValueError('unrecognised form specifier: {0}'.format(form))


__version__ = get_version()

if __name__ == '__main__':
    print(get_version())
