"""Initializes a new basmati project"""
from logging import getLogger
from pathlib import Path

from basmati.basmati_project import BasmatiProject

logger = getLogger('basmati.init')

ARGS = [(['--example-project', '-e'], {'help': 'Initialize with example project'})]
RUN_OUTSIDE_PROJECT = True


def main(cmd_ctx, args):
    logger.info('Initializing new project')
    BasmatiProject.init(Path.cwd())
    if args.example_project:
        logger.info('Creating example project')
        raise NotImplemented()
