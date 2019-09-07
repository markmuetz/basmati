# coding: utf-8
import numpy as np

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

from basmati import BasmatiProject
from basmati.utils import coarse_grain2d
from basmati.hydrosheds import load_hydrosheds_dem


def plot_2d(ma_dem, title, filename, extent):
    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.title(title)
    ax.coastlines()
    ax.imshow(ma_dem[::-1, :], extent=extent, origin='lower')
    plt.savefig(f'figs/{filename}')

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
    project = BasmatiProject()
    bounds, tx, dem, mask = load_hydrosheds_dem(project.hydrosheds_dir, 'as')
    extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    ma_dem = np.ma.masked_array(dem, mask)

    dem_coarse = coarse_grain2d(dem, (10, 10))
    ma_dem_coarse = np.ma.masked_array(dem_coarse, dem_coarse < -1000)

    plot_2d(ma_dem, 'DEM Asia at 30 s resolution (1 / 120 deg)', 'dem_asia_30s.png', extent)
    plot_2d(ma_dem_coarse, 
            'DEM Asia at 5 min resolution (1 / 12 deg)', 'dem_asia_5min.png', extent)

    # plot_3d(dem)
