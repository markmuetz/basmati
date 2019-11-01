from logging import getLogger
from pathlib import Path
from typing import Union, Iterable, Tuple, Set

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from numpy import ndarray
from pandas.core.base import PandasObject
from rasterio.transform import Affine

logger = getLogger('basmati.hydrosheds')

HYDROBASINS_FILE_TPL = 'hybas_{region}_lev{level:02}_v1c.shp'
HYDROSHEDS_DEM_FILE_TPL = '{region}_dem_{resolution}.bil'


def load_hydrobasins_geodataframe(hydrosheds_dir: Union[str, Path], region: str,
                                  levels: Iterable = range(1, 7),
                                  hydrobasins_file_tpl: str = HYDROBASINS_FILE_TPL) -> gpd.GeoDataFrame:
    """Load all data for the desired region and levels.

    :param hydrosheds_dir: directory of HydroSHEDS datasets
    :param region: 2 character region code
    :param levels: Pfafstetter levels to load
    :param hydrobasins_file_tpl: filename template
    :return: geodataframe containing all the data for the desired region and levels
    """
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


def load_hydrosheds_dem(hydrosheds_dir: Union[str, Path], region: str, resolution: str = '30s',
                        hydrosheds_dem_file_tpl: str = HYDROSHEDS_DEM_FILE_TPL) -> Tuple[ndarray, Affine,
                                                                                         ndarray, ndarray]:
    """Load a HydroSHEDS Digital Elevation Model (DEM).

    :param hydrosheds_dir: directory of HydroSHEDS datasets
    :param region: 2 character region code
    :param resolution: resolution to load
    :param hydrosheds_dem_file_tpl: filename template
    :return: bounds, affine transform, DEM and mask of the DEM
    """
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


def is_downstream(pfaf_id_a: Union[int, str], pfaf_id_b: Union[int, str]) -> bool:
    """Calculate if pfaf_id_b is downstream of pfaf_id_a

    Implemented as in https://en.wikipedia.org/wiki/Pfafstetter_Coding_System#Properties
    Works even if pfaf_id_a and pfaf_id_b are at different levels.

    :param pfaf_id_a: first Pfafstetter id (upstream)
    :param pfaf_id_b: second Pfafstetter id (downstream)
    :return: `True` if pfaf_id_b is downstream of pfaf_id_a, `False` otherwise or if a == b
    """
    if str(pfaf_id_a) == str(pfaf_id_b):
        # Basin is not downstream of itself.
        return False
    n = 0
    for c1, c2 in zip(str(pfaf_id_a), str(pfaf_id_b)):
        if c1 == c2:
            n += 1
        else:
            break
    # First n digits are the same.
    # In case where b is shorter than a (e.g. b is level 1, a is level 2), only compare the matching digits up to
    # the length of b.
    min_len_a_b = min(len(str(pfaf_id_a)), len(str(pfaf_id_b)))
    if int(str(pfaf_id_b)[n:min_len_a_b]) < int(str(pfaf_id_a)[n:min_len_a_b]):
        # If any remaining digits in b are even it is not downstream.
        for d in [int(c) for c in str(pfaf_id_b)[n:]]:
            if d % 2 == 0:
                return False
        return True
    return False


def _find_downstream(gdf: gpd.GeoDataFrame, start_basin_pfaf_id: int) -> gpd.GeoDataFrame:
    """Find all downstream basins at the same level as the start basin.

    Can also be used as a method on a `gpd.GeoDataFrame`:
    `gdf.find_downstream(start_basin_pfaf_id)`

    :param gdf: hydrobasins geodataframe to traverse
    :param start_basin_pfaf_id: Pfafstetter id of start basin
    :return: filtered geodataframe at level of start basin based on which basins are downstream of start basin
    """
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


def _find_upstream(gdf: gpd.GeoDataFrame, start_basin_pfaf_id: int) -> gpd.GeoDataFrame:
    """Find all upstream basins at the same level as the start basin.

    Can also be used as a method on a `gpd.GeoDataFrame`:
    `gdf.find_upstream(start_basin_pfaf_id)`

    :param gdf: hydrobasins geodataframe to traverse
    :param start_basin_pfaf_id: Pfafstetter id of start basin
    :return: filtered geodataframe at level of start basin based on which basins are upstream of start basin
    """
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


def _find_next_level_larger(gdf: gpd.GeoDataFrame, start_basin_pfaf_id: int) -> gpd.GeoDataFrame:
    """Find basin one level lower (i.e. found basin is larger).

    if `start_basin_pfaf_id == 913`, will return basin 91.
    Can return 0 or 1 basins.

    Can also be used as a method on a `gpd.GeoDataFrame`:
    `gdf.find_next_level_larger(start_basin_pfaf_id)`

    :param gdf: hydrobasins geodataframe to traverse
    :param start_basin_pfaf_id: Pfafstetter id of start basin
    :return: filtered geodataframe with 0 or 1 basins at level lower
    """
    assert isinstance(gdf, gpd.GeoDataFrame)
    larger_gdf = gdf[gdf.PFAF_STR == str(start_basin_pfaf_id)[:-1]]
    assert len(larger_gdf) <= 1  # can be zero.
    return larger_gdf


def _find_next_level_smaller(gdf: gpd.GeoDataFrame, start_basin_pfaf_id: int) -> gpd.GeoDataFrame:
    """Find basins one level higher (i.e. found basins are smaller).

    if `start_basin_pfaf_id == 91`, will return basins 911, 912... 919.
    Can return 0-9 basins.

    Can also be used as a method on a `gpd.GeoDataFrame`:
    `gdf.find_next_level_smaller(start_basin_pfaf_id)`

    :param gdf: hydrobasins geodataframe to traverse
    :param start_basin_pfaf_id: Pfafstetter id of start basin
    :return: filtered geodataframe with 0-9 basins at level higher
    """
    assert isinstance(gdf, gpd.GeoDataFrame)
    start_row = gdf[gdf.PFAF_ID == start_basin_pfaf_id].iloc[0]
    return gdf[gdf.PFAF_STR.str.startswith(str(start_basin_pfaf_id)) & (gdf.LEVEL == start_row.LEVEL + 1)]


def _area_select(gdf: gpd.GeoDataFrame, min_area: float, max_area: float) -> gpd.GeoDataFrame:
    """Select basins from lower to higher levels that are between min_area and max_area in area.

    Start by working out if any basins at e.g. level 1 are selected.
    Then move on to higher levels (smaller basins).
    At each level, only add basins if the basin at the level below has not been added.
    e.g. level 3 basins 411 to 419 will not be added if at level 2 basin 41 was added.

    Can also be used as a method on a `gpd.GeoDataFrame`:
    `gdf.area_select(min_area, max_area)`

    :param gdf: hydrobasins geodataframe to traverse
    :param min_area: minimum area of basin
    :param max_area: maximum area of basin
    :return: filtered geodataframe from any level (favouring lower levels) with area between min and max
    """
    all_good_index: Set[int] = set()
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
            
            if max_area > row.SUB_AREA > min_area:
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
PandasObject.find_next_level_larger = _find_next_level_larger
PandasObject.find_next_level_smaller = _find_next_level_smaller
PandasObject.area_select = _area_select
