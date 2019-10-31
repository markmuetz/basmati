import itertools
import os
import zipfile
from logging import getLogger
from pathlib import Path
from typing import Union

from basmati.basmati_errors import BasmatiError
from basmati.utils import sysrun

logger = getLogger('basmati.download')

DATASETS = ['ALL', 'hydrosheds_dem_30s', 'hydrobasins_all_levels']
HYDROBASINS_REGIONS = ['ALL', 'af', 'ar', 'as', 'au', 'eu', 'gr', 'na', 'sa', 'si']

# These URLs are stable, but they won't download with requests. They WILL download using wget though.
# Copied from: https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAI_jasMJPZl_6wX6d3vEOla?dl=0
HYDROSHEDS_URLS = {
    'hydrosheds_dem_30s': {
        'af': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB2aqcFLIqVo2aIrxxXlSdxa/'
               'HydroSHEDS_DEM/DEM_30s_BIL/af_dem_30s_bil.zip', 'af_dem_30s_bil.zip'),
        'as': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABCE7PbsmXH4pWoiXnLooRNa/'
               'HydroSHEDS_DEM/DEM_30s_BIL/as_dem_30s_bil.zip', 'as_dem_30s_bil.zip'),
        'au': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABRayBEd6B4s6ayQwjTdHdba/'
               'HydroSHEDS_DEM/DEM_30s_BIL/au_dem_30s_bil.zip', 'au_dem_30s_bil.zip'),
        'ca': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB5k5NMTevSo08qVJG3u34_a/'
               'HydroSHEDS_DEM/DEM_30s_BIL/ca_dem_30s_bil.zip', 'ca_dem_30s_bil.zip'),
        'eu': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB37xAq8GE7htebBvgS3DPTa/'
               'HydroSHEDS_DEM/DEM_30s_BIL/eu_dem_30s_bil.zip', 'eu_dem_30s_bil.zip'),
        'na': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADOB5dtqwWdkruat6T3hU_2a/'
               'HydroSHEDS_DEM/DEM_30s_BIL/na_dem_30s_bil.zip', 'na_dem_30s_bil.zip'),
        'sa': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACLgapv6MTaRWs-MTEeZNXRa/'
               'HydroSHEDS_DEM/DEM_30s_BIL/sa_dem_30s_bil.zip', 'sa_dem_30s_bil.zip'),
    },
    'hydrobasins_all_levels': {
        'af': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADo046FqiQlMrjFwfYjhlFSa/'
               'HydroBASINS/standard/af/hybas_af_lev01-12_v1c.zip', 'hybas_af_lev01-12_v1c.zip'),
        'as': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAloxuhEEFdoYfY4ZB-ikTma/'
               'HydroBASINS/standard/as/hybas_as_lev01-12_v1c.zip', 'hybas_as_lev01-12_v1c.zip'),
        'au': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABm11_TQtXvWMxm5yo6p7y9a/'
               'HydroBASINS/standard/au/hybas_au_lev01-12_v1c.zip', 'hybas_au_lev01-12_v1c.zip'),
        'eu': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABAwy_KMsRm9cRJWqo24JhBa/'
               'HydroBASINS/standard/eu/hybas_eu_lev01-12_v1c.zip', 'hybas_eu_lev01-12_v1c.zip'),
        'gr': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAB8rkuyt2jJ1iticE4mC9BQa/'
               'HydroBASINS/standard/gr/hybas_gr_lev01-12_v1c.zip', 'hybas_gr_lev01-12_v1c.zip'),
        'na': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAA2M3Kn5lRfu50t8LY-YQJEa/'
               'HydroBASINS/standard/na/hybas_na_lev01-12_v1c.zip', 'hybas_na_lev01-12_v1c.zip'),
        'sa': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADhV7E60JvMCwqFqJrqBzN_a/'
               'HydroBASINS/standard/sa/hybas_sa_lev01-12_v1c.zip', 'hybas_sa_lev01-12_v1c.zip'),
        'si': ('https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABQ7aOlIb5PVHF9xPx0WQ81a/'
               'HydroBASINS/standard/si/hybas_si_lev01-12_v1c.zip', 'hybas_si_lev01-12_v1c.zip'),
    }
}


def download_file_wget(url: str, basedir: Path, filename: Path) -> Path:
    """Downloads a file from a given URL to the desired basedir / filename.

    Uses wget and system command because requests cannot resolve the redirects of the
    stable dropbox links used by HydroSHEDS.
    See here for the base Dropbox directory:
    https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAAI_jasMJPZl_6wX6d3vEOla?dl=0

    :param url: URL where file can be downloaded
    :param basedir: directory to download to
    :param filename: filename of file to download
    :return: filepath of downloaded file
    """
    filepath = basedir / filename
    if filepath.exists():
        raise BasmatiError(f'{filepath} already exists')
    cmd = f'wget {url} -O {filepath}'
    logger.debug(cmd)
    resp = sysrun(cmd)
    logger.debug(resp)
    logger.debug(resp.stdout)

    return filepath


def unzip_file(basedir: Path, zipfilepath: Path) -> None:
    """Completely extract a zip file to a given basedir

    :param basedir: directory to extract to
    :param zipfilepath: path to zipfile
    """
    with zipfile.ZipFile(zipfilepath, 'r') as zip_ref:
        zip_ref.extractall(str(basedir))


class UnrecognizedRegionError(BasmatiError):
    pass


class HydroshedsDownloader:
    """Downloads and unzips HydroSHEDS dataset files from Dropbox
    """
    # N.B. more restrictive than HYDROBASINS_REGIONS
    hydrosheds_30s_regions = ['af', 'ar', 'as', 'au', 'eu', 'na', 'sa']

    def __init__(self, hydrosheds_dir: Union[str, Path], delete_zip: bool) -> None:
        """Creates instance to download data to a given hydrosheds_dir.

        :param hydrosheds_dir: directory to download data to - must exist
        :raises: BasmatiError if hydrosheds_dir does not exist
        :param delete_zip: delete zipfiles after download and extract
        """
        self.hydrosheds_dir = Path(hydrosheds_dir)
        self.delete_zip = delete_zip
        if not self.hydrosheds_dir.exists():
            raise BasmatiError(f'{self.hydrosheds_dir} does not exist')

    def _unzip_file(self, filename: Path) -> None:
        logger.info(f'Unzipping {filename}')
        unzip_file(self.hydrosheds_dir, filename)
        if self.delete_zip:
            logger.info(f'Deleting {filename}')
            filename.unlink()

    def download_hydrosheds_dem_30s(self, region: str) -> None:
        """Download 30s Digital Elevation Model for region.

        :param region: region to download DEM for
        """
        if region not in self.hydrosheds_30s_regions:
            msg = (f'Unrecognized region: {region}, must be one of:'
                   f'{", ".join(self.hydrosheds_30s_regions)}')
            raise UnrecognizedRegionError(msg)

        url, filename = HYDROSHEDS_URLS['hydrosheds_dem_30s'][region]
        logger.info(f'Downloading from {url}')
        filepath = download_file_wget(url, self.hydrosheds_dir, Path(filename))
        logger.info(f'Downloaded {filepath}')

        if filepath.suffix == '.zip':
            self._unzip_file(filepath)

    def download_hydrobasins_all_levels(self, region: str) -> None:
        """Download HydroBASINS dataset, levels 1-12.

        :param region: region to download dataset for
        """
        if region not in HYDROBASINS_REGIONS:
            msg = (f'Unrecognized region: {region}, must be one of:'
                   f'{", ".join(self.hydrosheds_30s_regions)}')
            raise UnrecognizedRegionError(msg)

        url, filename = HYDROSHEDS_URLS['hydrobasins_all_levels'][region]
        logger.info(f'Downloading from {url}')
        filepath = download_file_wget(url, self.hydrosheds_dir, Path(filename))
        logger.info(f'Downloaded {filepath}')

        if filepath.suffix == '.zip':
            self._unzip_file(filepath)


def download_main(dataset: str, region: str, delete_zip: bool) -> None:
    """Entry point for downloading HydroSHEDS datasets for the given region

    Relies on HYDROSHEDS_DIR env var being set.

    e.g.:
    $ basmati download -d <dataset> -r <region>

    :raises: BasmatiError if HYDROSHEDS_DIR not set
    :raises: BasmatiError region or dataset not recognized
    :param dataset: HydroSHEDS dataset to download
    :param region: 2 character region code
    :param delete_zip: delete downloaded zipfiles after extract
    """
    hydrosheds_dir = os.getenv('HYDROSHEDS_DIR')
    if not hydrosheds_dir:
        msg = 'env var HYDROSHEDS_DIR not set'
        logger.error(msg)
        logger.info('Set this variable to the HydroSHEDS data directory.')
        logger.info('Downloaded datasets will be saved here.')
        raise BasmatiError(msg)

    if dataset not in DATASETS:
        msg = f'Unrecognized dataset, must be one of: {", ".join(DATASETS)}'
        logger.error(msg)
        raise BasmatiError(msg)

    if region not in HYDROBASINS_REGIONS:
        msg = f'Unrecognized region, must be one of: {", ".join(HYDROBASINS_REGIONS)}'
        logger.error(msg)
        raise BasmatiError(msg)

    hydrosheds_dirpath = Path(hydrosheds_dir)
    if not hydrosheds_dirpath.exists():
        logger.info(f'Creating {hydrosheds_dirpath}')
        hydrosheds_dirpath.mkdir(parents=True)

    downloader = HydroshedsDownloader(hydrosheds_dirpath, delete_zip)
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
