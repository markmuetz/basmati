# coding: utf-8
from pathlib import Path

import rasterio
import numpy as np

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

from coarse_grain2d import coarse_grain2d

HYDROSHEDS_DIR = '/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroSHEDS'

def load_dem30s():
    with rasterio.open(Path(HYDROSHEDS_DIR, 'as_dem_30s.bil')) as as_dem:
    # as_dem = rasterio.open(Path(HYDROSHEDS_DIR, 'as_dem_30s.bil'))
        # N.B. in different order to rasterio tx!
        gdal_tx = np.array(as_dem.get_transform())
        affine_tx = rasterio.transform.Affine(gdal_tx[1], gdal_tx[2], gdal_tx[0], 
                                              gdal_tx[4], gdal_tx[5], gdal_tx[3]) 
        # print(as_dem.bounds)
        # print(gdal_tx.reshape(2, 3))
        dem = as_dem.read()[0]
        ma_dem = np.ma.masked_array(dem, ~as_dem.dataset_mask())
    return dem, ma_dem, affine_tx

def plot_2d(ma_dem, title):
    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title(title)
    ax.coastlines()
    ax.imshow(ma_dem[::-1, :], extent=(55, 180, -10, 60), origin='lower')
    plt.show()

def plot_3d(dem):
    dem_coarse = coarse_grain2d(dem, (10, 10))
    dem_coarse[dem_coarse < 0] = 0

    x = np.linspace(55, 180, 1500)
    y = np.linspace(-10, 60, 840)
    X, Y = np.meshgrid(x, y, indexing='xy')

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, dem_coarse[::-1, :], cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    ax.set_zlim((0, 20000))
    plt.show()

if __name__ == '__main__':
    dem, ma_dem, affine_tx = load_dem30s()

    dem_coarse = coarse_grain2d(dem, (10, 10))
    dem_coarse[dem_coarse < 0] = 0

    plot_2d(ma_dem, 'DEM Asia at 30 s resolution (1 / 120 deg)')
    plot_2d(dem_coarse, 'DEM Asia at 5 min resolution (1 / 12 deg)')
    plot_3d(dem)
