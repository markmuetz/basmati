# coding: utf-8
# get_ipython().run_line_magic('run', 'build_raster.py')
# get_ipython().run_line_magic('run', 'hb3.py')
# get_ipython().run_line_magic('run', 'disp_dem.py')
import numpy as np
import matplotlib.pyplot as plt

from build_raster import build_raster
from hb3 import load_hydrobasins_geodataframe
from disp_dem import load_dem30s

HYDROBASINS_DIR = '/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/as/'

if __name__ == '__main__':
    gdf = load_hydrobasins_geodataframe(HYDROBASINS_DIR, 'as', range(1, 6))
    dem, ma_dem, affine_tx = load_dem30s()

    gdf4 = gdf[gdf.LEVEL == 4]
    raster = build_raster(gdf4.geometry, dem.shape, affine_tx)

    fig, ax = plt.subplots()
    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))
    extent=(55, 180, -10, 60)
    ax.imshow(np.ma.masked_array(dem, raster != 47), extent=extent)
    gdf[(gdf.LEVEL == 5) & gdf.PFAF_STR.str.startswith('4349')].geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=0.5)
    plt.title('DEM of 4349')
    plt.xlim((90, 115))
    plt.ylim((20, 40))
