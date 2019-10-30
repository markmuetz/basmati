# import logging
# Need to make sure that this is set to log something
# before everything else starts trying to get the logger.
# logging.basicConfig()  # nopep8

from .version import VERSION
from .setup_logging import setup_logger
from .basmati_errors import BasmatiError
# Time consuming. Leave as: from basmati import hydrosheds
# from .hydrosheds import load_hydrobasins_geodataframe, load_hydrosheds_dem

__version__ = VERSION
__all__ = [
    setup_logger,
    BasmatiError,
]
