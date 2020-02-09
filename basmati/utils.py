import subprocess as sp
from typing import List, Iterable

import numpy as np
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


def build_raster_from_geometries(geometries: Iterable[BaseGeometry],
                                 shape: Iterable[int], tx: Affine) -> np.ndarray:
    """Build a 2D raster from the geometries (e.g. `gdf.geometry`)

    Each geometry is assigned an index, which increments by one for each geometry.

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
