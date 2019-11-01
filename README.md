basmati [![Build Status](https://travis-ci.org/markmuetz/basmati.svg?branch=master)](https://travis-ci.org/markmuetz/basmati)
=======

Introduction
------------

basmati (BAsin-Scale Model Assessment Tool) is a tool that makes it easy to access the [HydroBASINS](https://www.hydrosheds.org/page/hydrobasins) global dataset of watershed boundaries, and to combine this with meteorological data such as precipitation. A command-line tool makes it easy to download datasets for any geographical region. HydroBASINS datasets are loaded as a [geopandas](http://geopandas.org/) `GeoDataFrame` object, and useful methods are to this, e.g. to find all basins which are upstream of a given basin or select basins of a given area. Utilites are provided to produce 2-dimensional rasters from the basins using [rasterio](https://rasterio.readthedocs.io/en/stable/).

Installation
------------

basmati depends on the following packages:

-- `geopandas`
-- `rasterio`
-- `shapely`
