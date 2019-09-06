import numpy as np
from scipy import ndimage

import rasterio
import rasterio.features


def build_raster_from_geometries(geometries, shape, tx):
    raster = np.zeros(shape, dtype=int)
    for i, geom in enumerate(geometries):
        if geom.geom_type == 'MultiPolygon':
            raster |= rasterio.features.rasterize(zip(geom, [i + 1] * len(geom)), shape, transform=tx)
        else:
            raster |= rasterio.features.rasterize(zip([geom], [i + 1]), shape, transform=tx)
    return raster


def coarse_grain2d(arr, grain_size):
    assert arr.shape[0] % grain_size[0] == 0
    assert arr.shape[1] % grain_size[1] == 0
    num0 = arr.shape[0] // grain_size[0]
    num1 = arr.shape[1] // grain_size[1]
    num_grains = num0 * num1
    index = np.arange(num_grains)
    labels = index.reshape((num0, num1)).repeat(grain_size[1], axis=1).repeat(grain_size[0], axis=0)
    return ndimage.mean(arr, labels=labels, index=index).reshape(num0, num1)
