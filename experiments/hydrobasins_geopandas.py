# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import cartopy.crs as ccrs

HYDROBASINS_DIR = '/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/as'


def find_downstream(gdf, start_row):
    next_row = start_row
    downstream = np.zeros(len(gdf), dtype=bool)

    while next_row is not None:
        next_downstream = np.array(next_row['NEXT_DOWN'] == gdf['HYBAS_ID'], dtype=bool)
        downstream |= next_downstream
        next_gdf = gdf[next_downstream]
        if len(next_gdf):
            assert len(next_gdf) == 1
            next_row = next_gdf.iloc[0]
        else:
            next_row = None

    return gdf[downstream]


def find_upstream(gdf, start_row):
    next_hops = np.array(gdf['NEXT_DOWN'] == start_row['HYBAS_ID'], dtype=bool)
    all_hops = next_hops.copy()
    while next_hops.sum():
        next_gdf = gdf.loc[next_hops]
        next_hops = np.zeros_like(next_hops)
        for i, row in next_gdf.iterrows():
            next_hops |= np.array(gdf['NEXT_DOWN'] == row['HYBAS_ID'], dtype=bool)
            all_hops |= next_hops 

    return gdf[all_hops > 0]

# def calc_hops_to_end(gdf, start_gdf):
#     next_gdf = start_gdf
#     for i, row in start_gdf.iterrows():
#         next_slice = gdf['NEXT_DOWN'] == row['HYBAS_ID']
#         gdf.loc[gdf_slice, 'HOPS_TO_END'] = row['HOPS_TO_END'] + 1
#         next_gdf = gdf[gdf_slice]
#         print(next_gdf)
# 
#         while len(next_gdf):
#             gdf_slice = gdf['NEXT_DOWN'] == row['HYBAS_ID']
#             gdf.loc[gdf_slice, 'HOPS_TO_END'] = row['HOPS_TO_END'] + 1
#             next_gdf = gdf[gdf_slice]
#             print(next_gdf)

if __name__ == '__main__':
    gdf = gpd.read_file(f'{HYDROBASINS_DIR}/hybas_as_lev08_v1c.shp')
    id_dist_max = gdf['DIST_MAIN'].idxmax()
    furthest = gdf.iloc[id_dist_max]

    downstream_furthest = find_downstream(gdf, furthest)
    coast_row = downstream_furthest.iloc[0]
    upstream = find_upstream(gdf, coast_row)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    upstream.plot(ax=ax)
    downstream_furthest.plot(ax=ax, color='g')

    id_up_area_max = gdf['UP_AREA'].idxmax()
    find_upstream(gdf, gdf.loc[id_up_area_max]).plot(ax=ax, color='red')

    gdf[gdf['NEXT_DOWN'] == 0].plot(ax=ax, color='k')

    plt.show()
