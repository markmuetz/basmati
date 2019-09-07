.PHONY: all create_figs clean

default: all
all: create_figs 

create_figs: 
	python disp_dem.py
	python hydrobasins_geopandas.py
	python raster_dem_basin_overlay_4349.py

clean:
	rm -rf figs/*

