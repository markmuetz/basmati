import numpy as np
import rasterio
import rasterio.features

def build_raster(geometries, shape, tx):
    raster = np.zeros(shape, dtype=int)
    for i, geom in enumerate(geometries):
        if geom.geom_type == 'MultiPolygon':
            raster |= rasterio.features.rasterize(zip(geom, [i + 1] * len(geom)), shape, transform=tx)
        else:
            raster |= rasterio.features.rasterize(zip([geom], [i + 1]), shape, transform=tx)
    return raster


