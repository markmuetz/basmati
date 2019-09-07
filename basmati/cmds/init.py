"""Initializes a new basmati project"""
import os
from logging import getLogger
from pathlib import Path

from basmati.basmati_project import BasmatiProject

logger = getLogger('basmati.init')

ARGS = [(['--example-project', '-e'], {'help': 'Initialize with example project',
                                       'action': 'store_true'})]
RUN_OUTSIDE_PROJECT = True


def main(cmd_ctx, args):
    logger.info('Initializing new project')
    if args.example_project:
        project_dir = Path.cwd() / 'example_project'
        project_dir.mkdir()
        BasmatiProject.init(project_dir)
        logger.info('Creating example project')
        BasmatiProject.init_example_project(project_dir)
    else:
        BasmatiProject.init(Path.cwd())
