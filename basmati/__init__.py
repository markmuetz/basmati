from basmati.basmati_errors import BasmatiError
from basmati.setup_logging import setup_logger
from basmati.version import VERSION

# Time consuming. Leave as: from basmati import hydrosheds
# from basmati.hydrosheds import load_hydrobasins_geodataframe, load_hydrosheds_dem

__version__ = VERSION
__all__ = [
    'setup_logger',
    'BasmatiError',
]
