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

class HydroBASINS:
    def __init__(self, hydrobasins_dir, continent):
        self.hydrobasins_dir = hydrobasins_dir
        self.continent = continent
        self.gdf = None

    def load(self, levels=range(1, 13)):
        gdfs = []
        for level in levels:
            print(f'Loading level: {level}')
            filepath = Path(self.hydrobasins_dir, FILE_TPL.format(level=level))
            gdf = gpd.read_file(str(filepath))
            gdf['LEVEL'] = level
            gdfs.append(gdf)
        self.gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
        self.gdf['PFAF_STR'] = self.gdf.PFAF_ID.apply(str)

    def get_rows(self, **query):
        gdf = self.gdf
        for qkey, qval in query.items():
            if qkey[-4:] == '__lt':
                gdf = gdf[gdf[qkey[:-4]] < qval]
            elif qkey[-4:] == '__gt':
                gdf = gdf[gdf[qkey[:-4]] > qval]
            else:
                gdf = gdf[gdf[qkey] == qval]
        return gdf

    def get_row(self, **query):
        gdf = self.get_rows(**query)
        if len(gdf) == 0:
            raise Exception('Query returned no rows')
        elif len(gdf) > 2:
            raise Exception('Query returned multiple rows')
        return gdf.iloc[0]

    def find_downstream(self, start_row):
        gdf = self.gdf[self.gdf.LEVEL == start_row.LEVEL]
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

    def find_upstream(self, start_row):
        gdf = self.gdf[self.gdf.LEVEL == start_row.LEVEL]
        next_hops = np.array(gdf['NEXT_DOWN'] == start_row['HYBAS_ID'], dtype=bool)
        all_hops = next_hops.copy()
        while next_hops.sum():
            next_gdf = gdf.loc[next_hops]
            next_hops = np.zeros_like(next_hops)
            for i, row in next_gdf.iterrows():
                next_hops |= np.array(gdf['NEXT_DOWN'] == row['HYBAS_ID'], dtype=bool)
                all_hops |= next_hops 

        return gdf[all_hops > 0]

if __name__ == '__main__':
    hb = HydroBASINS('/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/as', 'as')
    hb.load(range(1, 7)) 
