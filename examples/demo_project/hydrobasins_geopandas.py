# coding: utf-8
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import basmati as bm


def plot_selected_basins(gdf):
    id_dist_max = gdf['DIST_MAIN'].idxmax()
    furthest = gdf.iloc[id_dist_max]

    downstream_furthest = gdf.find_downstream(furthest.PFAF_ID)
    coast_row = downstream_furthest.iloc[0]
    upstream = gdf.find_upstream(coast_row.PFAF_ID)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    upstream.plot(ax=ax)
    downstream_furthest.plot(ax=ax, color='g')

    id_up_area_max = gdf['UP_AREA'].idxmax()
    gdf.find_upstream(gdf.loc[id_up_area_max].PFAF_ID).plot(ax=ax, color='red')

    gdf[gdf['NEXT_DOWN'] == 0].plot(ax=ax, color='k')

    filename = 'hydrobains_level8_selected_basins.png'
    plt.savefig(f'figs/{filename}')


def plot_basin_area_stats(gdf):
    for level in sorted(gdf.LEVEL.unique()):
        plt.figure(f'SUB_AREA hist {level}')
        gdf_lev = gdf[gdf.LEVEL == level]
        gdf_lev.SUB_AREA.hist(bins=10)
        plt.ylabel('number')
        plt.xlabel('area (km$^2$)')
        plt.savefig(f'figs/sub_area_hist_{level}.png')

    df = pd.read_csv('schiemann2018mean_supplementary_tableS1.csv')
    plt.figure(f'Schiemann2018 hist')
    df.Area.hist(bins=10)
    plt.ylabel('number')
    plt.xlabel('area (km$^2$)')
    plt.savefig(f'figs/schiemann2018_sub_area_hist.png')


if __name__ == '__main__':
    project = bm.BasmatiProject()
    gdf = bm.load_hydrobasins_geodataframe(project.hydrosheds_dir, 'as', range(1, 9))

    plot_selected_basins(gdf[gdf.LEVEL == 8])
    plot_basin_area_stats(gdf)
