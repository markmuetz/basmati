# import logging
# Need to make sure that this is set to log something
# before everything else starts trying to get the logger.
# logging.basicConfig()  # nopep8

from .version import VERSION
from .setup_logging import setup_logger
from .basmati_cmd import main as basmati_main
from .basmati_project import BasmatiProject
from .basmati_errors import BasmatiError
# Time consuming. Leave as: from basmati import hydrosheds
# from .hydrosheds import load_hydrobasins_geodataframe, load_hydrosheds_dem

__version__ = VERSION

__all__ = [
    basmati_main,
    BasmatiProject,
    BasmatiError,
]
setup_logger()

def setup_ipython(logger_kwargs={}):
    """Injects useful variables into the global namespace. Only use interactively."""
    setup_logger(**logger_kwargs)

    import sys
    from collections import OrderedDict
    import __main__ as main
    # Thanks: http://stackoverflow.com/a/2356420/54557
    # Guard to check being called interactively:
    if hasattr(main, '__file__'):
        raise Exception('Should only be used interactively')
    # Thanks: http://stackoverflow.com/a/14298025/54557
    builtins = sys.modules['builtins'].__dict__

    project = BasmatiProject()
    globals_vars = OrderedDict()
    globals_vars['project'] = project
    print('Adding to global namespace:')
    for key, value in globals_vars.items():
        print('  ' + key)
        builtins[key] = value

