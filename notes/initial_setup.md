Initial setup
=============

* Installed jaspy: [https://github.com/cedadev/jaspy-manager]
..+ On breakeven, did this with root priveleges.
..+ On zg, did using ~/opt/jaspy as base dir (worked fine)
..+ Installed version given in instructions, think different from Jasmin version
* Installed rasterio using pip
* Downloaded HydroBASINS data manually.
..+ Requested dl link on breakeven
..+ Used dropbox on zg -- both worked fine although dropbox better for automating?

Initial expts
-------------

* Tried using python libs shapefile and geopandas to access data. Like geopandas best.
* Got to grips with Pfafstetter codes. Learnt how routing represented (easiest with gpd dataframe).
* Explored data.
* Did some basic rasterization: level 1 Asia and level 2 basins work. Thought about aliasing through oversampling.

