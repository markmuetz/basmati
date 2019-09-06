"""Downloads data for basmati project"""
from logging import getLogger
from pathlib import Path

from basmati.downloader import Downloader
from basmati.basmati_errors import BasmatiError

logger = getLogger('basmati.download')

ARGS = [(['--all-requires', '-a'], {'help': 'Download all files in requires sect (config)',
                                    'action': 'store_true'})]
RUN_OUTSIDE_PROJECT = False


def main(cmd_ctx, args):
    requires = cmd_ctx.project.config['requires']
    regions = [r.strip() for r in requires['regions'].split(',')]
    if args.all_requires:
        downloader = Downloader(cmd_ctx.project.hydrosheds_dir, )
        for region in regions:
            if 'hydrosheds_dem' in requires and requires['hydrosheds_dem'].lower() == 'yes':
                try:
                    downloader.download_hydrosheds_dem(region)
                except BasmatiError as be:
                    logger.error(f'{be}')
            if 'hydrobasins_all_levels' in requires and requires['hydrobasins_all_levels'].lower() == 'yes':
                try:
                    downloader.download_hydrobasins_all_levels(region)
                except BasmatiError as be:
                    logger.error(f'{be}')

