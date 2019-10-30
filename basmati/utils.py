import subprocess as sp

import numpy as np
from scipy import ndimage

from rasterio.features import rasterize


def sysrun(cmd):
    """Run a system command, returns a CompletedProcess

    raises CalledProcessError if cmd is bad.
    to access output: sysrun(cmd).stdout"""
    return sp.run(cmd, check=True, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf8') 


def build_raster_from_geometries(geometries, shape, tx):
    raster = np.zeros(shape, dtype=int)
    for i, geom in enumerate(geometries):
        if geom.geom_type == 'MultiPolygon':
            raster |= rasterize(zip(geom, [i + 1] * len(geom)), shape, transform=tx)
        else:
            raster |= rasterize(zip([geom], [i + 1]), shape, transform=tx)
    return raster


def coarse_grain2d(arr, grain_size):
    assert arr.shape[0] % grain_size[0] == 0
    assert arr.shape[1] % grain_size[1] == 0
    num0 = arr.shape[0] // grain_size[0]
    num1 = arr.shape[1] // grain_size[1]
    return arr.reshape(num0, grain_size[0], num1, grain_size[1]).mean(axis=(1, 3))


def coarse_grain2d_ndim(arr, grain_size):
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
