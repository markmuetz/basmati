import subprocess as sp
from typing import List
from collections.abc import Collection

import iris
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import Affine
from scipy import ndimage
from shapely.geometry.base import BaseGeometry


def sysrun(cmd: str) -> sp.CompletedProcess:
    """Run a system command

    Gets all output (stdout and stderr).
    To access output: `sysrun(cmd).stdout`

    :param cmd: command to run
    :raises: `sp.CalledProcessError`
    :return: result of cmd
    """
    return sp.run(cmd, check=True, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf8')


def build_raster_from_geometries(geometries: Collection[BaseGeometry],
                                 shape: Collection[int], tx: Affine) -> np.ndarray:
    """Build a 2D raster from the geometries (e.g. `gdf.geometry`)

    Each geometry is assigned an index, which increments by one for each geometry.
    In the returned raster, the cells corresponding to each geometry will be filled in with the appropriate index value.

    :param geometries: Individual geometries
    :param shape: shape of desired raster
    :param tx: affine transform to apply to each geometry before rasterizing
    :return: 2D raster where each index is the raster of an individual geometry.
    """
    raster = np.zeros(shape, dtype=int)
    for i, geom in enumerate(geometries):
        if geom.geom_type == 'MultiPolygon':
            geom_raster = rasterize(zip(geom, [i + 1] * len(geom)), shape, transform=tx)
        else:
            geom_raster = rasterize(zip([geom], [i + 1]), shape, transform=tx)
        assert (raster[geom_raster != 0] == 0).all(), 'overlapping geometries'
        raster |= geom_raster
    return raster


def build_raster_from_lon_lat(geometries: Collection[BaseGeometry],
                              lon_min: float, lon_max: float, lat_min: float, lat_max: float,
                              nlon: int, nlat: int) -> np.ndarray:
    """Build raster from lon/lat box with number in each direction specified

    Each geometry is assigned an index, which increments by one for each geometry.
    In the returned raster, the cells corresponding to each geometry will be filled in with the appropriate index value.

    :param geometries: Individual geometries
    :param lon_min: minimum longitude
    :param lon_max: maximum longitude
    :param lat_min: minimum latitude
    :param lat_max: maximum latitude
    :param nlon: number of longitudinal cells
    :param nlat: number of latitudinal cells
    :return: 2D raster where each index is the raster of an individual geometry.
    """
    scale_lon = (lon_max - lon_min) / nlon
    scale_lat = (lat_max - lat_min) / nlat

    affine_tx = rasterio.transform.Affine(scale_lon, 0, lon_min,
                                          0, scale_lat, lat_min)
    raster = build_raster_from_geometries(geometries,
                                          (nlat, nlon),
                                          affine_tx)
    return raster


def build_raster_from_cube(geometries: Collection[BaseGeometry], cube: iris.cube.Cube) -> np.ndarray:
    """Build raster from cube

    Each geometry is assigned an index, which increments by one for each geometry.
    In the returned raster, the cells corresponding to each geometry will be filled in with the appropriate index value.

    :param geometries: Individual geometries
    :param cube: target cube
    :return: 2D raster where each index is the raster of an individual geometry.
    """
    lat_max, lat_min, lon_max, lon_min, nlat, nlon = get_latlon_from_cube(cube)
    return build_raster_from_lon_lat(geometries, lon_min, lon_max, lat_min, lat_max, nlon, nlat)


def build_raster_cube_from_cube(geometries: Collection[BaseGeometry], cube: iris.cube.Cube, name: str) -> iris.cube.Cube:
    """Build raster from cube

    Each geometry is assigned an index, which increments by one for each geometry.
    In the returned raster, the cells corresponding to each geometry will be filled in with the appropriate index value.

    :param geometries: Individual geometries
    :param cube: target cube
    :param name: name of output cube
    :return: 2D raster where each index is the raster of an individual geometry.
    """
    raster = build_raster_from_cube(geometries, cube)
    longitude = cube.coord('longitude')
    latitude = cube.coord('latitude')

    raster_cube = iris.cube.Cube(raster, long_name=f'{name}', units='-',
                                 dim_coords_and_dims=[(latitude, 0),
                                                      (longitude, 1)])
    return raster_cube


def build_weights_from_lon_lat(geometries: Collection[BaseGeometry],
                               lon_min: float, lon_max: float, lat_min: float, lat_max: float,
                               nlon: int, nlat: int,
                               oversample_factor: int = 10) -> np.ndarray:
    """Build weights from lon/lat box with number in each direction specified and using the given oversample_factor

    In the returned weights array, first index is for individual weights. Each weight is for one geometry, and is
    between 0 and 1. All interior weights will be one, exterior 0. Weights where the geometry crosses a grid cell have
    a value which is calculated by oversampling the given raster based on the oversample_factor.

    :param geometries: Individual geometries
    :param lon_min: minimum longitude
    :param lon_max: maximum longitude
    :param lat_min: minimum latitude
    :param lat_max: maximum latitude
    :param nlon: number of longitudinal cells
    :param nlat: number of latitudinal cells
    :param oversample_factor: amount of additional cells to use in each direction when oversampling
    :return: 3D weights where each element of first index is weights for an individual geometry.
    """
    raster_highres = build_raster_from_lon_lat(geometries, lon_min, lon_max, lat_min, lat_max, nlon * oversample_factor,
                                               nlat * oversample_factor)
    raster_highres_reshaped = raster_highres.reshape(nlat, oversample_factor, nlon, oversample_factor)
    weights = np.zeros((len(geometries), nlat, nlon))
    for i in range(weights.shape[0]):
        weights[i] = (raster_highres_reshaped == (i + 1)).sum(axis=(1, 3)) / (oversample_factor**2)

    return weights


def build_weights_cube_from_cube(geometries: Collection[BaseGeometry], cube: iris.cube.Cube, name: str,
                                 oversample_factor: int = 10) -> iris.cube.Cube:
    """Build weights cube from target cube and using the given oversample_factor

    In the returned weights array, first index is for individual weights. Each weight is for one geometry, and is
    between 0 and 1. All interior weights will be one, exterior 0. Weights where the geometry crosses a grid cell have
    a value which is calculated by oversampling the given raster based on the oversample_factor.

    :param geometries: Individual geometries
    :param cube: target cube
    :param name: name of output weights cube.
    :param oversample_factor: amount of additional cells to use in each direction when oversampling
    :return: 3D weights where each element of first index is weights for an individual geometry.
    """
    lat_max, lat_min, lon_max, lon_min, nlat, nlon = get_latlon_from_cube(cube)

    weights = build_weights_from_lon_lat(geometries, lon_min, lon_max, lat_min, lat_max, nlon, nlat, oversample_factor)

    basin_index_coord = iris.coords.DimCoord(np.arange(len(geometries)), long_name='basin_index')
    longitude = cube.coord('longitude')
    latitude = cube.coord('latitude')

    weights_cube = iris.cube.Cube(weights, long_name=f'{name}', units='-',
                                  dim_coords_and_dims=[(basin_index_coord, 0),
                                                       (latitude, 1),
                                                       (longitude, 2)])

    return weights_cube


def get_latlon_from_cube(cube):
    """Return domain covered by cube, taking into account cell boundaries

    :param cube: target cube
    :return: tuple(lat_max, lat_min, lon_max, lon_min, nlat, nlon)
    """
    nlat = cube.shape[-2]
    nlon = cube.shape[-1]
    for latlon in ['latitude', 'longitude']:
        if not cube.coord(latlon).has_bounds():
            cube.coord(latlon).guess_bounds()
    longitude = cube.coord('longitude')
    latitude = cube.coord('latitude')
    lon_min, lon_max = longitude.bounds[0, 0], longitude.bounds[-1, 1]
    lat_min, lat_max = latitude.bounds[0, 0], latitude.bounds[-1, 1]
    return lat_max, lat_min, lon_max, lon_min, nlat, nlon


def coarse_grain2d(arr: np.ndarray, grain_size: List[int]) -> np.ndarray:
    """Coarse grain a 2D arr based on grain_size

    :param arr: array to coarse grain
    :param grain_size: 2 value size of grain
    :return: coarse-grained array
    """
    assert arr.shape[0] % grain_size[0] == 0
    assert arr.shape[1] % grain_size[1] == 0
    num0 = arr.shape[0] // grain_size[0]
    num1 = arr.shape[1] // grain_size[1]
    return arr.reshape(num0, grain_size[0], num1, grain_size[1]).mean(axis=(1, 3))


def coarse_grain2d_ndim(arr: np.ndarray, grain_size: List[int]) -> np.ndarray:
    """Coarse grain an N-D arr based on grain_size

    :param arr: array to coarse grain
    :param grain_size: N value size of grain
    :return: coarse-grained array
    """
    assert arr.shape[0] % grain_size[0] == 0
    assert arr.shape[1] % grain_size[1] == 0
    num0 = arr.shape[0] // grain_size[0]
    num1 = arr.shape[1] // grain_size[1]
    num_grains = num0 * num1
    index = np.arange(num_grains)
    labels = (index.reshape((num0, num1))
              .repeat(grain_size[1], axis=1)
              .repeat(grain_size[0], axis=0))
    return ndimage.mean(arr, labels=labels, index=index).reshape(num0, num1)
