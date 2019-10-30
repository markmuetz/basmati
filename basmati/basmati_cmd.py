import argparse

from .setup_logging import setup_logger
from .basmati_errors import BasmatiError
from .basmati_demo import demo_main
from .downloader import download_main, DATASETS, HYDROBASINS_REGIONS
from .version import get_version

def _parse_args(argv):
    parser = argparse.ArgumentParser(description='BASMATI command line tool')

    # Top-level arguments.
    parser.add_argument('--debug', '-D', help='Enable debug logging', action='store_true')
    parser.add_argument('--bw', '-B', help='Disable colour logging', action='store_true')
    parser.add_argument('--warn', '-W', help='Warn on stderr', action='store_true')

    subparsers = parser.add_subparsers(dest='subcmd_name')
    # name of subparser ends up in subcmd_name -- use for command dispatch.

    # demo
    demo_parser = subparsers.add_parser('demo', help='Run through BASMATI demo')

    # download
    download_parser = subparsers.add_parser('download', aliases=['dl'], 
                                            help='Download HydroSHEDS datasets')
    download_parser.add_argument('--dataset', '-d', 
                                 required=True,
                                 choices=DATASETS, 
                                 help='Dataset to download')
    download_parser.add_argument('--region', '-r', 
                                 required=True,
                                 choices=HYDROBASINS_REGIONS, 
                                 help='Region to download')
    download_parser.add_argument('--delete-zip',
                                 action='store_true',
                                 help='Delete zipfile after unpacking')

    # version
    version_parser = subparsers.add_parser('version', help='Print BASMATI version')
    version_parser.add_argument('--long', '-l', action='store_true', help='long version')

    args = parser.parse_args(argv[1:])

    return args


def basmati_cmd(argv, import_log_msg=None):
    args = _parse_args(argv)
    loglevel = 'DEBUG' if args.debug else 'INFO'

    logger = setup_logger(loglevel, not args.bw, args.warn)
    logger.debug(import_log_msg)
    logger.debug(argv)
    logger.debug(args)
    
    try:
        # Dispatch command.
        # N.B. args should always be dereferenced at this point,
        # not passed into any subsequent functions.
        if args.subcmd_name == 'demo':
            demo_main()
        elif args.subcmd_name == 'download':
            download_main(args.dataset, args.region, args.delete_zip)
        elif args.subcmd_name == 'version':
            print(get_version(form='long' if args.long else 'short'))

    except BasmatiError as be:
        logger.error(be)
        raise
    except Exception as e:
        logger.error(e)
        raise
