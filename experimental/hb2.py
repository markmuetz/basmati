from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

FILE_TPL = 'hybas_as_lev{level:02}_v1c.shp'


# class HydroBASINS(gpd.GeoDataFrame):

# Idea:? https://stackoverflow.com/questions/43504068/create-my-own-method-for-dataframes-python/53630084
# class HydroBASINS(gpd.GeoDataFrame):

# Or 
# from pandas.core.base import PandasObject
# def your_fun(df):
#         ...
#         PandasObject.your_fun = your_fun
# Will this work for GeoDataFrame?

class HydroBasinsDataFrame(gpd.GeoDataFrame):
    @staticmethod
    def load(hydrobasins_dir, continent, levels=range(1, 13)):
        raise Exception('Does not return HydroBasinsDataFrame on e.g. slice')
        gdfs = []
        for level in levels:
            print(f'Loading level: {level}')
            filepath = Path(hydrobasins_dir, FILE_TPL.format(level=level))
            gdf = gpd.read_file(str(filepath))
            gdf['LEVEL'] = level
            gdfs.append(gdf)
        hydf = HydroBasinsDataFrame(pd.concat(gdfs, ignore_index=True))
        hydf['PFAF_STR'] = hydf.PFAF_ID.apply(str)
        return hydf

    @property
    def _constructor(self):
        return HydroBasinsDataFrame

    def find_downstream(self, start_row_idx):
        start_row = self.loc[start_row_idx]
        gdf = self[self.LEVEL == start_row.LEVEL]
        next_row = start_row
        downstream = np.array(gdf.HYBAS_ID == start_row.HYBAS_ID, dtype=bool)

        while next_row is not None:
            next_downstream = np.array(next_row['NEXT_DOWN'] == gdf['HYBAS_ID'], dtype=bool)
            downstream |= next_downstream
            next_gdf = gdf[next_downstream]
            if len(next_gdf):
                assert len(next_gdf) == 1
                next_row = next_gdf.iloc[0]
            else:
                next_row = None

        return gdf[downstream]

    def find_upstream(self, start_row_idx):
        start_row = self.loc[start_row_idx]
        gdf = self[self.LEVEL == start_row.LEVEL]
        next_hops = np.array(gdf['NEXT_DOWN'] == start_row['HYBAS_ID'], dtype=bool)
        all_hops = next_hops.copy()
        while next_hops.sum():
            next_gdf = gdf.loc[next_hops]
            next_hops = np.zeros_like(next_hops)
            for i, row in next_gdf.iterrows():
                next_hops |= np.array(gdf['NEXT_DOWN'] == row['HYBAS_ID'], dtype=bool)
                all_hops |= next_hops 

        return gdf[all_hops > 0]

