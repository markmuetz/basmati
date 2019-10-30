import os
import logging
from pathlib import Path

from .demo.disp_dem import disp_dem
from .demo.hydrobasins_geopandas import hydrobasins_geopandas
from .demo.raster_dem_basin_overlay_4349 import basin_overlay_4349

logger = logging.getLogger(__name__)


def usage_message(logger):
    logger.info('You can use the following commands to download the data:')
    print('basmati download -d hydrosheds_dem_30s -r as')
    print('basmati download -d hydrobasins_all_levels -r as')
    logger.info('')
    logger.info('Alternatively, you can download HydroSHEDS data from:')
    logger.info('https://www.hydrosheds.org/downloads')
    logger.info('For this demo, the Asia (as) DEM and and HydroBASINS data are required.')
    logger.info('For the DEM, Select:')
    logger.info('  Void-filled elevation (GRID and BIL format)')
    logger.info('    Elevation 30sec resolution BIL')
    logger.info('      as_dem_30s_bil.zip')
    logger.info('For HydroBASINS, Select:')
    logger.info('  HydroBASINS')
    logger.info('    Standard (without lakes)')
    logger.info('      Central and South-East Asia')
    logger.info('        hybas_as_lev01-12_v1c.zip')
    logger.info('')
    logger.info('Unzip to a directory, and the set HYDROSHEDS_DIR env var, e.g.')
    logger.info('export HYDROSHEDS_DIR=/home/user/HydroSHEDS')


def demo_main():
    logger.info('Running BASMATI demo')
    logger.info('====================')

    if not os.getenv('HYDROSHEDS_DIR'):
        logger.error('env var HYDROSHEDS_DIR not set')
        logger.info('Set this variable to the HydroSHEDS data directory')
        logger.info('')
        usage_message(logger)
        return

    figsdir = Path('basmati_demo_figs')
    if not figsdir.exists():
        logger.info(f'Creating dir: {figsdir}')
        figsdir.mkdir()

    try:
        disp_dem()
        hydrobasins_geopandas()
        basin_overlay_4349()
    except Exception as e:
        logger.error(e)
        usage_message(logger)
        return

    logger.info('=============================')
    logger.info('Successfully ran BASMATI demo')
    logger.info(f'Have a look in the {figsdir} dir for the output')
