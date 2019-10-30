# coding: utf-8
import os
import logging

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from basmati.utils import coarse_grain2d
from basmati.hydrosheds import load_hydrosheds_dem

logger = logging.getLogger(__name__)


def plot_dem(ma_dem, title, filename, extent):
    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title(title)
    ax.coastlines()
    ax.imshow(ma_dem[::-1, :], extent=extent, origin='lower')
    output_filename = f'basmati_demo_figs/{filename}'
    logger.info(f'Saving figure to: {output_filename}')
    plt.savefig(output_filename)


def disp_dem():
    logger.info(f'Running {__file__}: disp_dem()')
    hydrosheds_dir = os.getenv('HYDROSHEDS_DIR')
    bounds, tx, dem, mask = load_hydrosheds_dem(hydrosheds_dir, 'as')
    extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    ma_dem = np.ma.masked_array(dem, mask)

    dem_coarse = coarse_grain2d(dem, (10, 10))
    ma_dem_coarse = np.ma.masked_array(dem_coarse, dem_coarse < -1000)

    plot_dem(ma_dem, 'DEM Asia at 30 s resolution (1 / 120 deg)', 'dem_asia_30s.png', extent)
    plot_dem(ma_dem_coarse, 
             'DEM Asia at 5 min resolution (1 / 12 deg)', 'dem_asia_5min.png', extent)
    plt.close('all')
