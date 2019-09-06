"""Initializes a new basmati project"""
# from logging import getLogger
from pathlib import Path

from basmati.basmati_project import BasmatiProject

# logger = getLogger('basmati.init')

# ARGS = [(['--suite-type', '-t'], {'help': 'type of suite'})]
ARGS = []
RUN_OUTSIDE_PROJECT = True


def main(cmd_ctx, args):
    BasmatiProject.init(Path.cwd())
