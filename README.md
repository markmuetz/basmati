basmati [![Build Status](https://travis-ci.org/markmuetz/basmati.svg?branch=master)](https://travis-ci.org/markmuetz/basmati) [![codecov](https://codecov.io/gh/markmuetz/basmati/branch/master/graph/badge.svg)](https://codecov.io/gh/markmuetz/basmati) 
=======

Introduction
------------

basmati (BAsin-Scale Model Assessment ToolkIt) is a tool that makes it easy to access the [HydroBASINS](https://www.hydrosheds.org/page/hydrobasins) global dataset of watershed boundaries, and to combine this with meteorological data such as precipitation. A command-line tool makes it easy to download datasets for any geographical region. HydroBASINS datasets are loaded as a [geopandas](http://geopandas.org/) `GeoDataFrame` objects, and useful methods are added to this to e.g. find all basins which are upstream of a given basin or select basins of a given area. Utilites are provided to produce 2-dimensional rasters from the basins using [rasterio](https://rasterio.readthedocs.io/en/stable/).

Documentation is available at [Read the Docs](http://basmati.readthedocs.io/en/latest/).

Installation
------------

An [installation guide](https://basmati.readthedocs.io/en/latest/installation.html) gives details on how to install basmati. basmati depends on the following packages:

- `geopandas`
- `rasterio`
- `shapely`

Examples
--------

```bash
export HYDROSHEDS_DIR=$HOME/HydroSHEDS
# Download all datasets for Asia (as)
basmati download --dataset ALL -r as
```

```python
>>> import os
>>> from basmati.hydrosheds import load_hydrobasins_geodataframe
>>> hb_gdf = load_hydrobasins_geodataframe(os.getenv('HYDROSHEDS_DIR'), 'as', [1, 2, 3])  # load levels 1-3
>>> print(hb_gdf[hb_gdf.LEVEL == 2].SUB_AREA.max())
4740420.0
```

See the [quickstart guide](https://basmati.readthedocs.io/en/latest/quickstart.html) for more examples.
