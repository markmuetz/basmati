import os
from logging import getLogger
from pathlib import Path
import itertools
import zipfile

import requests

from .basmati_errors import BasmatiError
from .utils import sysrun

logger = getLogger('basmati.download')

# These URLs are stable, but they won't download with requests. They WILL download using wget though.
# Copied from: https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAI_jasMJPZl_6wX6d3vEOla?dl=0

DATASETS = ['ALL', 'hydrosheds_dem_30s', 'hydrobasins_all_levels']
HYDROBASINS_REGIONS = ['ALL', 'af', 'ar', 'as', 'au', 'eu', 'gr', 'na', 'sa', 'si']

HYDROSHEDS_URLS = {
    'hydrosheds_dem_30s': {
        'af': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB2aqcFLIqVo2aIrxxXlSdxa/HydroSHEDS_DEM/DEM_30s_BIL/af_dem_30s_bil.zip', 'af_dem_30s_bil.zip'),
        'as': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABCE7PbsmXH4pWoiXnLooRNa/HydroSHEDS_DEM/DEM_30s_BIL/as_dem_30s_bil.zip', 'as_dem_30s_bil.zip'),
        'au': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABRayBEd6B4s6ayQwjTdHdba/HydroSHEDS_DEM/DEM_30s_BIL/au_dem_30s_bil.zip', 'au_dem_30s_bil.zip'),
        'ca': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB5k5NMTevSo08qVJG3u34_a/HydroSHEDS_DEM/DEM_30s_BIL/ca_dem_30s_bil.zip', 'ca_dem_30s_bil.zip'),
        'eu': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB37xAq8GE7htebBvgS3DPTa/HydroSHEDS_DEM/DEM_30s_BIL/eu_dem_30s_bil.zip', 'eu_dem_30s_bil.zip'),
        'na': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADOB5dtqwWdkruat6T3hU_2a/HydroSHEDS_DEM/DEM_30s_BIL/na_dem_30s_bil.zip', 'na_dem_30s_bil.zip'),
        'sa': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACLgapv6MTaRWs-MTEeZNXRa/HydroSHEDS_DEM/DEM_30s_BIL/sa_dem_30s_bil.zip', 'sa_dem_30s_bil.zip'),
    },
    'hydrobasins_all_levels': {
        'af': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADo046FqiQlMrjFwfYjhlFSa/HydroBASINS/standard/af/hybas_af_lev01-12_v1c.zip', 'hybas_af_lev01-12_v1c.zip'),
        'as': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAloxuhEEFdoYfY4ZB-ikTma/HydroBASINS/standard/as/hybas_as_lev01-12_v1c.zip', 'hybas_as_lev01-12_v1c.zip'),
        'au': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABm11_TQtXvWMxm5yo6p7y9a/HydroBASINS/standard/au/hybas_au_lev01-12_v1c.zip', 'hybas_au_lev01-12_v1c.zip'),
        'eu': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABAwy_KMsRm9cRJWqo24JhBa/HydroBASINS/standard/eu/hybas_eu_lev01-12_v1c.zip', 'hybas_eu_lev01-12_v1c.zip'),
        'gr': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB8rkuyt2jJ1iticE4mC9BQa/HydroBASINS/standard/gr/hybas_gr_lev01-12_v1c.zip', 'hybas_gr_lev01-12_v1c.zip'),
        'na': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAA2M3Kn5lRfu50t8LY-YQJEa/HydroBASINS/standard/na/hybas_na_lev01-12_v1c.zip', 'hybas_na_lev01-12_v1c.zip'),
        'sa': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADhV7E60JvMCwqFqJrqBzN_a/HydroBASINS/standard/sa/hybas_sa_lev01-12_v1c.zip', 'hybas_sa_lev01-12_v1c.zip'),
        'si': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABQ7aOlIb5PVHF9xPx0WQ81a/HydroBASINS/standard/si/hybas_si_lev01-12_v1c.zip', 'hybas_si_lev01-12_v1c.zip'),
    }
}


# Thanks:
# https://stackoverflow.com/a/16696317/54557
def download_file_python(basedir, url, filename):
    filename = basedir / filename
    if filename.exists():
        raise BasmatiError(f'{filename} already exists')

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    return filename


def download_file_wget(basedir, url, filename):
    filename = basedir / filename
    if filename.exists():
        raise BasmatiError(f'{filename} already exists')
    cmd = f'wget {url} -O {filename}'
    logger.debug(cmd)
    resp = sysrun(cmd)
    logger.debug(resp)
    logger.debug(resp.stdout)

    return filename


def unzip_file(basedir, filename):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(str(basedir))

class UnrecognizedRegionError(BasmatiError):
    pass

class HydroshedsDownloader:
    hydrosheds_30s_regions = ['af', 'ar', 'as', 'au', 'eu', 'na', 'sa']

    def __init__(self, hydrosheds_dir, delete_zip):
        self.hydrosheds_dir = Path(hydrosheds_dir)
        self.delete_zip = delete_zip
        if not self.hydrosheds_dir.exists():
            raise BasmatiError(f'{self.hydrosheds_dir} does not exist')

    def _unzip_file(self, filename):
        logger.info(f'Unzipping {filename}')
        unzip_file(self.hydrosheds_dir, filename)
        if self.delete_zip:
            logger.info(f'Deleting {filename}')
            filename.unlink()

    def download_hydrosheds_dem_30s(self, region):
        if region not in self.hydrosheds_30s_regions:
            msg = (f'Unrecognized region: {region}, must be one of:'
                   f'{", ".join(self.hydrosheds_30s_regions)}')
            raise UnrecognizedRegionError(msg)

        url, filename = HYDROSHEDS_URLS['hydrosheds_dem_30s'][region]
        logger.info(f'Downloading from {url}')
        filename = download_file_wget(self.hydrosheds_dir, url, filename)
        logger.info(f'Downloaded {filename}')

        if filename.suffix == '.zip':
            self._unzip_file(filename)

    def download_hydrobasins_all_levels(self, region):
        if region not in self.hydrosheds_30s_regions:
            msg = (f'Unrecognized region: {region}, must be one of:'
                   f'{", ".join(self.hydrosheds_30s_regions)}')
            raise UnrecognizedRegionError(msg)

        url, filename = HYDROSHEDS_URLS['hydrobasins_all_levels'][region]
        logger.info(f'Downloading from {url}')
        filename = download_file_wget(self.hydrosheds_dir, url, filename)
        logger.info(f'Downloaded {filename}')

        if filename.suffix == '.zip':
            self._unzip_file(filename)


def download_main(dataset, region, delete_zip):
    hydrosheds_dir = os.getenv('HYDROSHEDS_DIR')
    if not hydrosheds_dir:
        logger.error('env var HYDROSHEDS_DIR not set')
        logger.info('Set this variable to the HydroSHEDS data directory.')
        logger.info('Downloaded datasets will be saved here.')
        return

    if dataset not in DATASETS:
        logger.error(f'Unrecognized dataset, must be one of: {", ".join(DATASETS)}')
        return

    hydrosheds_dir = Path(hydrosheds_dir)
    if not hydrosheds_dir.exists():
        logger.info(f'Creating {hydrosheds_dir}')
        hydrosheds_dir.mkdir(parents=True)

    downloader = HydroshedsDownloader(hydrosheds_dir, delete_zip)
    if dataset == 'ALL':
        datasets = DATASETS[1:]
    else:
        datasets = [dataset]
    if region == 'ALL':
        regions = HYDROBASINS_REGIONS[1:]
    else:
        regions = [region]

    for dataset, region in itertools.product(datasets, regions):
        logger.info(f'Downloading: {dataset}, {region}')

        try:
            if dataset == 'hydrosheds_dem_30s':
                downloader.download_hydrosheds_dem_30s(region)
            elif dataset == 'hydrobasins_all_levels':
                downloader.download_hydrobasins_all_levels(region)
        except UnrecognizedRegionError:
            logger.info(f'  {dataset} {region} not found')

