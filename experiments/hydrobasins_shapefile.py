"""Experimental script to try out loading HydroBASINS data with shapefile"""
import sys

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import shapefile 

HYDROBASINS_DIR = '/home/markmuetz/mirrors/jasmin/cosmic/mmuetz/HydroBASINS/as'


def load_shapefile(level):
    return shapefile.Reader(f'{HYDROBASINS_DIR}/hybas_as_lev{level:02}_v1c.shp')


def plot_basin(min_level, max_level, target_pfid, plot_kwargs={}):
    assert min_level >= 1
    # assert len(target_pfid) >= max_level

    title = f'Basin {target_pfid}, min level {min_level}, max level {max_level}'
    plt.figure(title)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_title(title)

    for level in range(min_level, max_level + 1):
        shpfile = load_shapefile(level)
        if level == 1:
            bbox = shpfile.bbox
            ax.plot([bbox[0], bbox[2]], [bbox[1], bbox[1]], 'k-')
            ax.plot([bbox[0], bbox[2]], [bbox[3], bbox[3]], 'k-')
            ax.plot([bbox[0], bbox[0]], [bbox[1], bbox[3]], 'k-')
            ax.plot([bbox[2], bbox[2]], [bbox[1], bbox[3]], 'k-')

        pfid_level = min(len(target_pfid), level)

        n = shpfile.numRecords
        for i in range(n):
            shape = shpfile.shape(i)
            record = shpfile.record(i)

            pfid = str(record[8])
            if pfid[:pfid_level] != target_pfid[:pfid_level]:
                continue

            print(f'{i + 1}/{n}')
            geo_int = shape.__geo_interface__

            if geo_int['type'] == 'Polygon':
                mean_x, mean_y = [], []
                for polygon in geo_int['coordinates']:
                    # assert polygon[0] == polygon[-1]
                    arr = np.array(polygon)
                    ax.plot(arr[:, 0], arr[:, 1], **plot_kwargs)
                    mean_x.extend(arr[-1:, 0])
                    mean_y.extend(arr[-1:, 1])
                ax.text(arr[:, 0].mean(), arr[:, 1].mean(), f'{pfid}')

            elif geo_int['type'] == 'MultiPolygon':
                mean_x, mean_y = [], []
                for multi_polygon in geo_int['coordinates']:
                    for polygon in multi_polygon:
                        # assert polygon[0] == polygon[-1]
                        arr = np.array(polygon)
                        ax.plot(arr[:, 0], arr[:, 1], **plot_kwargs)
                        mean_x.extend(arr[:-1, 0])
                        mean_y.extend(arr[:-1, 1])

                ax.text(np.array(mean_x).mean(), np.array(mean_y).mean(), f'{pfid}')
            else:
                raise Exception(f'Unknown type {geo_int["type"]}')
    plt.show()


def plot_level(level, ax=None, plot_kwargs={}):
    shpfile = load_shapefile(level)

    if not ax:
        plt.figure()
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.set_title(f'Level {level:02}')
    # ax.set_xlim((-180, 180))
    # ax.set_ylim((-90, 90))
    bbox = shpfile.bbox

    ax.plot([bbox[0], bbox[2]], [bbox[1], bbox[1]], 'k-')
    ax.plot([bbox[0], bbox[2]], [bbox[3], bbox[3]], 'k-')
    ax.plot([bbox[0], bbox[0]], [bbox[1], bbox[3]], 'k-')
    ax.plot([bbox[2], bbox[2]], [bbox[1], bbox[3]], 'k-')

    n = shpfile.numRecords
    for i in range(n):
        shape = shpfile.shape(i)
        record = shpfile.record(i)
        pfid = record[8]
        print(f'{i + 1}/{n}')
        geo_int = shape.__geo_interface__

        if geo_int['type'] == 'Polygon':
            mean_x, mean_y = [], []
            for polygon in geo_int['coordinates']:
                # assert polygon[0] == polygon[-1]
                arr = np.array(polygon)
                ax.plot(arr[:, 0], arr[:, 1], **plot_kwargs)
                mean_x.extend(arr[-1:, 0])
                mean_y.extend(arr[-1:, 1])
            ax.text(arr[:, 0].mean(), arr[:, 1].mean(), f'{pfid}')

        elif geo_int['type'] == 'MultiPolygon':
            mean_x, mean_y = [], []
            for multi_polygon in geo_int['coordinates']:
                for polygon in multi_polygon:
                    # assert polygon[0] == polygon[-1]
                    arr = np.array(polygon)
                    ax.plot(arr[:, 0], arr[:, 1], **plot_kwargs)
                    mean_x.extend(arr[:-1, 0])
                    mean_y.extend(arr[:-1, 1])

            ax.text(np.array(mean_x).mean(), np.array(mean_y).mean(), f'{pfid}')
        else:
            raise Exception(f'Unknown type {geo_int["type"]}')
    

def plot_levels():
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_title(f'Levels: 1, 2, 3')

    plot_level(3, ax, {'color': 'g', 'linewidth': 1})
    plot_level(2, ax, {'color': 'b', 'linewidth': 2})
    plot_level(1, ax, {'color': 'k', 'linewidth': 3})

    plt.show()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'level':
            plot_level(int(sys.argv[2]))
            plt.show()
        elif sys.argv[1] == 'levels':
            plot_levels()
            plt.show()
        elif sys.argv[1] == 'basin':
            plot_basin(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
            plt.show()
