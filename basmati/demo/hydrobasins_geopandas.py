# coding: utf-8
import os
import logging
from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from basmati.hydrosheds import load_hydrobasins_geodataframe

logger = logging.getLogger(__name__)


def plot_selected_basins(hb_gdf):
    id_dist_max = hb_gdf['DIST_MAIN'].idxmax()
    furthest = hb_gdf.loc[id_dist_max]

    downstream_furthest = hb_gdf.find_downstream(furthest.PFAF_ID)
    coast_row = downstream_furthest.iloc[0]
    upstream = hb_gdf.find_upstream(coast_row.PFAF_ID)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    upstream.plot(ax=ax)
    downstream_furthest.plot(ax=ax, color='yellow')

    id_up_area_max = hb_gdf['UP_AREA'].idxmax()
    hb_gdf.find_upstream(hb_gdf.loc[id_up_area_max].PFAF_ID).plot(ax=ax, color='red')

    hb_gdf[hb_gdf['NEXT_DOWN'] == 0].plot(ax=ax, color='k')

    output_filename = 'basmati_demo_figs/hydrobasins_level8_selected_basins.png'
    logger.info(f'Saving figure to: {output_filename}')
    plt.savefig(output_filename)


def plot_basin_area_stats(hb_gdf):
    for level in sorted(hb_gdf.LEVEL.unique()):
        plt.figure(f'SUB_AREA hist {level}')
        hb_gdf_lev = hb_gdf[hb_gdf.LEVEL == level]
        hb_gdf_lev.SUB_AREA.hist(bins=10)
        plt.ylabel('number')
        plt.xlabel('area (km$^2$)')
        plt.savefig(f'basmati_demo_figs/sub_area_hist_{level}.png')

    curr_dirpath = Path(__file__).parent
    csv_filepath = curr_dirpath/ 'schiemann2018mean_supplementary_tableS1.csv'
    logger.debug(f'loading CSV from: {csv_filepath}')

    df = pd.read_csv(str(csv_filepath))
    plt.figure(f'Schiemann2018 hist')
    df.Area.hist(bins=10)
    plt.ylabel('number')
    plt.xlabel('area (km$^2$)')
    output_filename = 'basmati_demo_figs/schiemann2018_sub_area_hist.png'
    logger.info(f'Saving figure to: {output_filename}')
    plt.savefig(output_filename)


def hydrobasins_geopandas():
    logger.info(f'Running {__file__}: hydrobasins_geopandas()')
    hydrosheds_dir = os.getenv('HYDROSHEDS_DIR')
    hb_gdf = load_hydrobasins_geodataframe(hydrosheds_dir, 'as', range(1, 9))

    plot_selected_basins(hb_gdf[hb_gdf.LEVEL == 8])
    plot_basin_area_stats(hb_gdf)
    plt.close('all')
