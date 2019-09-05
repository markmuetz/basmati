from pathlib import Path

import numpy as np
import pandas as pd
from pandas.core.base import PandasObject
import geopandas as gpd

FILE_TPL = 'hybas_as_lev{level:02}_v1c.shp'


def load_hydrobasins_geodataframe(hydrobasins_dir, continent, levels=range(1, 13)):
    gdfs = []
    for level in levels:
        print(f'Loading level: {level}')
        filepath = Path(hydrobasins_dir, FILE_TPL.format(level=level))
        gdf = gpd.read_file(str(filepath))
        gdf['LEVEL'] = level
        gdfs.append(gdf)
    gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    gdf['PFAF_STR'] = gdf.PFAF_ID.apply(str)
    return gdf


# Added to the GeoDataFrame class using:
# https://stackoverflow.com/a/53630084/54557
def _find_downstream(gdf, start_basin_idx):
    """Find all downstream basins at the same level as the start basin"""
    start_row = gdf.loc[start_basin_idx]
    gdf_lev = gdf[gdf.LEVEL == start_row.LEVEL]
    next_row = start_row
    downstream = np.array(gdf_lev.HYBAS_ID == start_row.HYBAS_ID, dtype=bool)

    while next_row is not None:
        next_downstream = np.array(next_row['NEXT_DOWN'] == gdf_lev['HYBAS_ID'], dtype=bool)
        downstream |= next_downstream
        next_gdf = gdf_lev[next_downstream]
        if len(next_gdf):
            assert len(next_gdf) == 1
            next_row = next_gdf.iloc[0]
        else:
            next_row = None

    return gdf_lev[downstream]


def _find_upstream(gdf, start_basin_idx):
    start_row = gdf.loc[start_basin_idx]
    gdf_lev = gdf[gdf.LEVEL == start_row.LEVEL]
    next_hops = np.array(gdf_lev['NEXT_DOWN'] == start_row['HYBAS_ID'], dtype=bool)
    all_hops = next_hops.copy()
    while next_hops.sum():
        next_gdf = gdf_lev.loc[next_hops]
        next_hops = np.zeros_like(next_hops)
        for i, row in next_gdf.iterrows():
            next_hops |= np.array(gdf_lev['NEXT_DOWN'] == row['HYBAS_ID'], dtype=bool)
            all_hops |= next_hops 

    return gdf_lev[all_hops > 0]


PandasObject.find_downstream = _find_downstream
PandasObject.find_upstream = _find_upstream
