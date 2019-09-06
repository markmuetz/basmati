from logging import getLogger
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.core.base import PandasObject

import geopandas as gpd
import rasterio

logger = getLogger('basmati.hydrosheds')

HYDROBASINS_FILE_TPL = 'hybas_{region}_lev{level:02}_v1c.shp'
HYDROSHEDS_DEM_FILE_TPL = '{region}_dem_{resolution}.bil'


def load_hydrobasins_geodataframe(hydrosheds_dir, region, levels=range(1, 13)):
    gdfs = []
    for level in levels:
        logger.info(f'Loading hydrobasins region: {region}; level: {level}')
        filename = HYDROBASINS_FILE_TPL.format(region=region, level=level)
        filepath = Path(hydrosheds_dir, filename)
        gdf = gpd.read_file(str(filepath))
        gdf['LEVEL'] = level
        gdfs.append(gdf)
    gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    gdf['PFAF_STR'] = gdf.PFAF_ID.apply(str)
    return gdf


def load_hydrosheds_dem(hydrosheds_dir, region, resolution='30s'):
    filename = HYDROSHEDS_DEM_FILE_TPL.format(region=region, resolution=resolution)
    logger.info(f'Loading hydrosheds DEM region: {region}; resolution: {resolution}')
    with rasterio.open(Path(hydrosheds_dir, filename)) as dem_buf:
        # N.B. in different order to rasterio tx!
        gdal_tx = np.array(dem_buf.get_transform())
        affine_tx = rasterio.transform.Affine(gdal_tx[1], gdal_tx[2], gdal_tx[0], 
                                              gdal_tx[4], gdal_tx[5], gdal_tx[3]) 
        dem = dem_buf.read()[0]
        mask = ~dem_buf.dataset_mask()
        bounds = dem_buf.bounds
    return bounds, affine_tx, dem, mask


# Added to the GeoDataFrame class using:
# https://stackoverflow.com/a/53630084/54557
def _find_downstream(gdf, start_basin_pfaf_id):
    """Find all downstream basins at the same level as the start basin"""
    assert isinstance(gdf, gpd.GeoDataFrame)
    start_row = gdf[gdf.PFAF_ID == start_basin_pfaf_id].iloc[0]
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


def _find_upstream(gdf, start_basin_pfaf_id):
    assert isinstance(gdf, gpd.GeoDataFrame)
    start_row = gdf[gdf.PFAF_ID == start_basin_pfaf_id].iloc[0]
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
