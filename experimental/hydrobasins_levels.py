from math import floor, ceil

import numpy as np
from scipy.interpolate import interp1d   

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from basmati import BasmatiProject
from basmati.hydrosheds import load_hydrobasins_geodataframe, load_hydrosheds_dem
from basmati.utils import build_raster_from_geometries

def get_levels_for_furthest(hb_gdf):
    id_dist_max = hb_gdf[hb_gdf.LEVEL == 8]['DIST_MAIN'].idxmax()
    furthest = hb_gdf.iloc[id_dist_max]
    pfaf_str = furthest.PFAF_STR

    pfaf_selector = ((hb_gdf.LEVEL == 1) & hb_gdf.PFAF_STR.str.startswith(pfaf_str[:1]))
    for i in range(2, 9):
        pfaf_selector |= ((hb_gdf.LEVEL == i) & hb_gdf.PFAF_STR.str.startswith(pfaf_str[:i]))
        print(pfaf_selector.sum())

    hb_gdf_pfaf = hb_gdf[pfaf_selector]
    bounds = hb_gdf_pfaf.geometry.bounds 
    extents = bounds.values[:, [0, 2, 1, 3]]
    return hb_gdf_pfaf, extents

def plot_levels(ma_dem, dem_extent, hb_gdf_pfaf, vals, extents, aspect):
    for i in range(len(extents)):
        print(i)
        val = vals[i]
        level = ceil(val)
        curr_level = floor(val)
        fig, ax = plt.subplots()

        ax.imshow(ma_dem, extent=dem_extent, cmap='terrain', vmin=-2000, vmax=8000)
        hb_gdf_pfaf.geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=0.5)
        hb_gdf_pfaf[hb_gdf_pfaf.LEVEL == level].geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=2)
        plt.title(f'Level {level}')
        if aspect is not None:
            dx = extents[i, 1] - extents[i, 0]
            dy = extents[i, 3] - extents[i, 2]

            extent_aspect = dx / dy
            if extent_aspect < aspect:
                new_dx = dy * aspect
                extents[i, 0] -= (new_dx - dx) / 2
                extents[i, 1] += (new_dx - dx) / 2
            elif extent_aspect > aspect:
                new_dy = dx / aspect
                extents[i, 2] -= (new_dy - dy) / 2
                extents[i, 3] += (new_dy - dy) / 2

        plt.xlim(extents[i, :2])
        plt.ylim(extents[i, 2:])

        plt.savefig(f'figs/level_anim{i:03d}.png')
        plt.close('all')

if __name__ == '__main__':
    project = BasmatiProject()
    hb_gdf = load_hydrobasins_geodataframe(project.hydrosheds_dir, 'as', range(1, 9))
    bounds, tx, dem, mask = load_hydrosheds_dem(project.hydrosheds_dir, 'as')
    dem_extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    aspect = 1.7

    hb_gdf1 = hb_gdf[hb_gdf.LEVEL == 1]
    raster = build_raster_from_geometries(hb_gdf1.geometry, dem.shape, tx)
    ma_dem = np.ma.masked_array(dem, raster == 0)
    n_per_level = 24
    N = 7 * n_per_level
    x = np.linspace(1, 8, 7 * n_per_level)
    slider = np.zeros_like(x)
    for i in range(7):
        slider[i * n_per_level: (i + 1) * n_per_level] = -0.5 * np.cos((x[:n_per_level] - 1) * np.pi) + 1.5 + i

    hb_gdf_pfaf, extents = get_levels_for_furthest(hb_gdf)
    f = interp1d(np.linspace(1, 8, 8), extents, axis=0, kind='linear')

    new_extents = f(slider)
    new_extents += np.array([-0.5, 0.5, -0.5, 0.5])[None, :] * np.linspace(1, 0.1, N)[:, None]
    plot_levels(ma_dem, dem_extent, hb_gdf_pfaf, slider, new_extents, aspect)
