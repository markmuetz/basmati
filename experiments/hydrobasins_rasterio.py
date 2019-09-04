# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd

import rasterio
import rasterio.features


def display_raster_level1():
    gdf = gpd.read_file('/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/hybas_as_lev01_v1c.shp')
    raster = build_raster(gdf.geometry)
    plot_raster(raster)

    raster = build_raster(gdf.geometry, 10)
    plot_raster(raster)

    raster = build_raster(gdf.geometry, 50)
    plot_raster(raster)

    return 

    geom = gdf.iloc[0].geometry
    tx = rasterio.transform.Affine(1, 0, -180, 0, 1, -90)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.imshow(rasterio.features.rasterize(zip(geom, [1] * len(geom)), (180, 360), all_touched=True, transform=tx), origin='lower', extent=(-180, 180, -90, 90))
    ax.coastlines()
    plt.show()

    tx = rasterio.transform.Affine(0.1, 0, -180, 0, 0.1, -90)

    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.imshow(rasterio.features.rasterize(zip(geom, [1] * len(geom)), (1800, 3600), all_touched=True, transform=tx), origin='lower', extent=(-180, 180, -90, 90))
    ax.coastlines()
    plt.show()

    tx = rasterio.transform.Affine(0.01, 0, -180, 0, 0.01, -90)

    plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.imshow(rasterio.features.rasterize(zip(geom, [1] * len(geom)), (18000, 36000), all_touched=True, transform=tx), origin='lower', extent=(-180, 180, -90, 90))
    ax.coastlines()
    plt.show()

def build_raster(geometries, scale=1):
    nlon = 180 * scale
    nlat = 360 * scale
    raster = np.zeros((nlon, nlat), dtype=int)
    tx = rasterio.transform.Affine(1 / scale, 0, -180, 0, 1 / scale, -90)
    for i, geom in enumerate(geometries):
        if geom.geom_type == 'MultiPolygon':
            raster |= rasterio.features.rasterize(zip(geom, [i + 1] * len(geom)), (nlon, nlat), transform=tx)
        else:
            raster |= rasterio.features.rasterize(zip([geom], [i + 1]), (nlon, nlat), transform=tx)
    return raster

def plot_raster(raster):
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.imshow(raster, extent=(-180, 180, -90, 90))
    ax.coastlines()
    plt.show()
    
def display_raster_level2():
    gdf = gpd.read_file('/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/hybas_as_lev02_v1c.shp')

    raster = build_raster(gdf.geometry)
    plot_raster(raster)

    raster = build_raster(gdf.geometry, 10)
    plot_raster(raster)

    raster = build_raster(gdf.geometry, 50)
    plot_raster(raster)

if __name__ == '__main__':
    display_raster_level1()
    display_raster_level2()
