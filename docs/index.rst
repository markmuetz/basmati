.. basmati documentation master file, created by
   sphinx-quickstart on Thu Oct 31 16:56:50 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

basmati |version|
=================

basmati (BAsin-Scale Model Assessment Tool) is a tool for analysing meteorological data from model simulations and observations over scale-selective and decision-relevant scales. It uses the HydroBASINS dataset of hydrological catchment basins to produce rasters that can be used to filter gridded precipitation data based on selected basins. Basins can be selected using a number of criteria, for example basins can be selected based on their area across different Pfafstetter levels so that they are between a desired minimum and maximum area.

The code is available in the `basmati github repository <https://github.com/markmuetz/basmati>`_.

.. toctree::   
    :maxdepth: 2
    :caption: Getting started:

    installation
    quickstart
    gallery

.. toctree::   
    :maxdepth: 2
    :caption: Reference:

    basmati_package



Index
=====

* :ref:`genindex`
