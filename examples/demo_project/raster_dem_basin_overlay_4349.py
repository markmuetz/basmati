import numpy as np
import matplotlib.pyplot as plt

import basmati as bm
from basmati.utils import build_raster_from_geometries


if __name__ == '__main__':
    project = bm.BasmatiProject()
    gdf = bm.load_hydrobasins_geodataframe(project.hydrosheds_dir, 'as', range(4, 6))
    bounds, tx, dem, mask = bm.load_hydrosheds_dem(project.hydrosheds_dir, 'as')
    extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    gdf4 = gdf[gdf.LEVEL == 4]
    raster = build_raster_from_geometries(gdf4.geometry, dem.shape, tx)

    fig, ax = plt.subplots()
    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))
    ax.imshow(np.ma.masked_array(dem, raster != 47), extent=extent)
    gdf[(gdf.LEVEL == 5) & gdf.PFAF_STR.str.startswith('4349')].geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=0.5)

    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))

    filename = 'dem_of_pfaf_id_4349.png'
    plt.savefig(f'figs/{filename}')

