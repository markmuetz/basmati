from logging import getLogger
from pathlib import Path
import zipfile

import requests

from basmati.basmati_errors import BasmatiError

logger = getLogger('basmati.download')

HYDROSHEDS_URLS = {
    'hydrosheds_dem': {
        'as': ('https://uc0ca0bebf19f2ac9c1a6b5a3b13.dl.dropboxusercontent.com/cd/0/get/AoCjZ2PmbuDIvSGh6Xu6t-OWw4aMfawl6lFu1dkkBebORJfczbp7V12rjzn33xG5nvOSbr2P_tmlPW381Cw_w_2GXUYa1gCSXNUs0k2wNWED6Q/file?_download_id=09588877458444256604178050994672991259002524015881458563406970418&_notify_domain=www.dropbox.com&dl=1', 'as_dem_30s_bil.zip'),
    },
    'hydrobasins_all_levels': {
        'as': ('https://uc218cc7f73d826f4eaf1bce4cb2.dl.dropboxusercontent.com/cd/0/get/AoCViSdSbGsoX68TerRdP71oic0aLPeEnCekOB7UJA-EAmRUFmt3vsxBozZh2KsiMb8I52PknTcszqaraAJmISlRP9BcqyNcsywlwv4QcpJr9w/file?_download_id=1067985919701944876956069376527172677577719082656302104088280771&_notify_domain=www.dropbox.com&dl=1', 'hybas_as_lev01-12_v1c.zip'),
    }
}


# Thanks:
# https://stackoverflow.com/a/16696317/54557
def download_file(basedir, url, filename):
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


def unzip_file(basedir, filename):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(str(basedir))


class Downloader:
    # regions = ['af', 'ar', 'as', 'au', 'eu', 'gr', 'na', 'sa', 'si']
    regions = ['as']
    def __init__(self, hydrosheds_dir):
        self.hydrosheds_dir = Path(hydrosheds_dir)
        if not self.hydrosheds_dir.exists():
            raise BasmatiError(f'{self.hydrosheds_dir} does not exist')

    def _check_region(self, region):
        if region not in self.regions:
            raise BasmatiError(f'Unrecognized region: {region}, must be {", ".join(self.regions)}')

    def download_hydrosheds_dem(self, region):
        self._check_region(region)
        url, filename = HYDROSHEDS_URLS['hydrosheds_dem'][region]
        logger.info(f'Downloading from {url}')
        filename = download_file(self.hydrosheds_dir, url, filename)
        if filename.suffix == '.zip':
            unzip_file(self.hydrosheds_dir, filename)



    def download_hydrobasins_all_levels(self, region):
        self._check_region(region)
        url, filename = HYDROSHEDS_URLS['hydrobasins_all_levels'][region]
        logger.info(f'Downloading from {url}')
        filename = download_file(self.hydrosheds_dir, url, filename)
        if filename.suffix == '.zip':
            unzip_file(self.hydrosheds_dir, filename)

