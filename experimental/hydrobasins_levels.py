from math import floor, ceil

import numpy as np
from scipy.interpolate import interp1d   

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from basmati import BasmatiProject
from basmati.hydrosheds import load_hydrobasins_geodataframe

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

def plot_levels(hb_gdf_pfaf, vals, extents):
    for i in range(len(extents)):
        print(i)
        plt.clf()
        val = vals[i]
        curr_level = floor(val)

        ax = hb_gdf_pfaf.geometry.boundary.plot(color=None, edgecolor='k', linewidth=0.5)
        hb_gdf_pfaf[hb_gdf_pfaf.LEVEL == curr_level + 1].geometry.boundary.plot(ax=ax, color=None, edgecolor='k', linewidth=2)
        level = ceil(val)
        plt.title(f'Level {level}')
        plt.xlim(extents[i, :2])
        plt.ylim(extents[i, 2:])
        plt.savefig(f'figs/level_anim{i:03d}.png')

if __name__ == '__main__':
    project = BasmatiProject()
    hb_gdf = load_hydrobasins_geodataframe(project.hydrosheds_dir, 'as', range(1, 9))

    hb_gdf_pfaf, extents = get_levels_for_furthest(hb_gdf)
    f = interp1d(np.linspace(1, 8, 8), extents, axis=0, kind='quadratic')
    vals = np.linspace(1, 8, 24 * 5)

    new_extents = f(vals)
    new_extents += np.array([-0.5, 0.5, -0.5, 0.5])[None, :] * np.linspace(1, 0.1, 24 * 5)[:, None]
    plot_levels(hb_gdf_pfaf, vals, new_extents)
