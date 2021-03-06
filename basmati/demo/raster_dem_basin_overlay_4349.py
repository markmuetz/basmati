import logging
import os

import matplotlib.pyplot as plt
import numpy as np

from basmati.hydrosheds import load_hydrobasins_geodataframe, load_hydrosheds_dem
from basmati.utils import build_raster_from_geometries

logger = logging.getLogger(__name__)

def basin_overlay_4349():
    logger.info(f'Running {__file__}: basin_overlay_4349()')
    hydrosheds_dir = os.getenv('HYDROSHEDS_DIR')
    hb_gdf = load_hydrobasins_geodataframe(hydrosheds_dir, 'as', range(4, 6))
    bounds, tx, dem, mask = load_hydrosheds_dem(hydrosheds_dir, 'as')
    extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    hb_gdf4 = hb_gdf[hb_gdf.LEVEL == 4]
    raster = build_raster_from_geometries(hb_gdf4.geometry, dem.shape, tx)

    fig, ax = plt.subplots()
    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))
    ax.imshow(np.ma.masked_array(dem, raster != 47), extent=extent)
    hb_gdf[(hb_gdf.LEVEL == 5) & hb_gdf.PFAF_STR.str.startswith('4349')]\
        .geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=0.5)

    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))

    output_filename = 'basmati_demo_figs/dem_of_pfaf_id_4349.png'
    logger.info(f'Saving figure to: {output_filename}')
    plt.savefig(output_filename)
    plt.close('all')
