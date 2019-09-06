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

def plot_2d(ma_dem):
    print(as_dem.bounds)

    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title('DEM Asia at 30 s resolution (1 / 120 deg)')
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
    with rasterio.open(Path(HYDROSHEDS_DIR, 'as_dem_30s.bil')) as as_dem:
        dem = as_dem.read()[0]
        ma_dem = np.ma.masked_array(dem, ~as_dem.dataset_mask())

    plot_2d(ma_dem)
    plot_3d(dem)
