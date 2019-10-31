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


def load_hydrobasins_geodataframe(hydrosheds_dir, region, levels=range(1, 7),
                                  hydrobasins_file_tpl=HYDROBASINS_FILE_TPL):
    if not Path(hydrosheds_dir).exists():
        raise OSError(f'{hydrosheds_dir} does not exist')
    crss = []
    gdfs = []
    for level in levels:
        filename = hydrobasins_file_tpl.format(region=region, level=level)
        filepath = Path(hydrosheds_dir, filename)
        if not filepath.exists():
            raise OSError(f'{filepath} does not exist')
        logger.debug(f'Loading hydrobasins region: {region}; level: {level}; {filepath}')
        gdf = gpd.read_file(str(filepath))
        crss.append(gdf.crs)
        gdf['LEVEL'] = level
        gdfs.append(gdf)

    # CRS is the Coordinate Reference System.
    # http://geopandas.org/projections.html
    assert all(crs == crss[0] for crs in crss[1:]), f'All CRS info not identical: {crss}'
    # The HydroBASINS data is all in epsg:4326, which is lat/lon:
    # https://spatialreference.org/ref/epsg/4326/
    # This is the same as WGS84.
    assert crss[0] == {'init': 'epsg:4326'}, f'Unexpected CRS: {crss[0]}'

    # N.B. CRS data is lost on pd.concat.
    gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    logger.debug(f'Setting CRS to {crss[0]}')
    gdf.crs = crss[0]
    gdf['PFAF_STR'] = gdf.PFAF_ID.apply(str)
    return gdf


def load_hydrosheds_dem(hydrosheds_dir, region, resolution='30s',
                        hydrosheds_dem_file_tpl=HYDROSHEDS_DEM_FILE_TPL):
    filename = hydrosheds_dem_file_tpl.format(region=region, resolution=resolution)
    logger.debug(f'Loading hydrosheds DEM region: {region}; resolution: {resolution}; {filename}')
    with rasterio.open(Path(hydrosheds_dir, filename)) as dem_buf:
        # N.B. in different order to rasterio tx!
        gdal_tx = np.array(dem_buf.get_transform())
        affine_tx = rasterio.transform.Affine(gdal_tx[1], gdal_tx[2], gdal_tx[0], 
                                              gdal_tx[4], gdal_tx[5], gdal_tx[3]) 
        dem = dem_buf.read()[0]
        mask = ~dem_buf.dataset_mask()
        bounds = dem_buf.bounds
    return bounds, affine_tx, dem, mask


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


def _find_next_larger(gdf, start_basin_pfaf_id):
    assert isinstance(gdf, gpd.GeoDataFrame)
    larger_gdf = gdf[gdf.PFAF_STR == str(start_basin_pfaf_id)[:-1]]
    assert len(larger_gdf) <= 1  # can be zero.
    return larger_gdf


def _find_next_smaller(gdf, start_basin_pfaf_id):
    assert isinstance(gdf, gpd.GeoDataFrame)
    start_row = gdf[gdf.PFAF_ID == start_basin_pfaf_id].iloc[0]
    return gdf[gdf.PFAF_STR.str.startswith(str(start_basin_pfaf_id)) & (gdf.LEVEL == start_row.LEVEL + 1)]


def _area_select(gdf, min_area, max_area):
    all_good_index = set()
    good_index = set()

    for level in range(gdf.LEVEL.min(), gdf.LEVEL.max() + 1):
        gdf_lev = gdf[gdf.LEVEL == level]

        gdf_too_large = gdf_lev[gdf.SUB_AREA > max_area]
        gdf_just_right = gdf_lev[(gdf.SUB_AREA <= max_area) & (gdf.SUB_AREA >= min_area)]
        gdf_too_small = gdf_lev[gdf.SUB_AREA < min_area]

        logger.debug(f'Level {level}')
        logger.debug(f'  too large: {len(gdf_too_large)}')
        logger.debug(f'  just right: {len(gdf_just_right)}')
        logger.debug(f'  too small: {len(gdf_too_small)}')

        if len(gdf_just_right) == 0:
            logger.debug(f'Skipping level: {level}')
            continue

        for irow_index in range(len(gdf_lev)):
            row_index = gdf_lev.index[irow_index]
            row = gdf_lev.iloc[irow_index]
            
            if row.SUB_AREA < max_area and row.SUB_AREA > min_area:
                larger_basin = gdf.find_next_larger(row.PFAF_ID)
                larger_basin_index = larger_basin.index[0] if len(larger_basin) else -1
                if larger_basin_index not in all_good_index:
                    good_index.add(row_index)
                all_good_index.add(row_index)

    return gdf.loc[good_index]


# Added to the GeoDataFrame class using:
# https://stackoverflow.com/a/53630084/54557
PandasObject.find_downstream = _find_downstream
PandasObject.find_upstream = _find_upstream
PandasObject.find_next_larger = _find_next_larger
PandasObject.find_next_smaller = _find_next_smaller
PandasObject.area_select = _area_select
