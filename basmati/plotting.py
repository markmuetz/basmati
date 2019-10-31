import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np


def plot_raster_with_coast(title, extent, raster, mask=None, reverse_y=False):
    plt.figure(title)
    ax = plt.axes(projection=ccrs.PlateCarree())

    plt.title(title)
    if mask is not None:
        raster = np.ma.masked_array(raster, mask)

    if reverse_y:
        raster = raster[::-1, :]

    ax.coastlines()
    ax.imshow(raster, extent=extent, origin='lower')
    plt.show()
