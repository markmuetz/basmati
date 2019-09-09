import os
import shutil
from pathlib import Path
from configparser import ConfigParser
from logging import getLogger

import basmati
from basmati.basmati_errors import BasmatiError
from basmati.setup_logging import setup_logger, add_file_logging

logger = getLogger('basmati.bm_project')


class BasmatiProject:
    dotbasmati_dir = Path('.basmati')

    @staticmethod
    def basmati_project_dir(path):
        while not BasmatiProject._is_project_root_dir(path):
            path = path.parent
            if path == Path('/'):
                # at root dir: /
                return None
        return path

    @staticmethod
    def _is_project_root_dir(path):
        if (path / BasmatiProject.dotbasmati_dir).exists():
            return True
        return False

    @staticmethod
    def init(project_dir):
        try:
            (project_dir / BasmatiProject.dotbasmati_dir).mkdir()
        except FileExistsError:
            raise BasmatiError('Project already initialized')

    @staticmethod
    def init_example_project(project_dir):
        basmati_home = Path(os.path.realpath(__file__)).parent
        example_project_dir = basmati_home / 'examples/example_project'
        assert example_project_dir.exists(), f'{example_project_dir} does not exist'
        logger.debug(f'cp files from {example_project_dir} to {project_dir}')

        filenames = list(example_project_dir.glob('*.py'))
        filenames.extend(list(example_project_dir.glob('*.csv')))
        filenames.extend(list(example_project_dir.glob('*.conf')))
        filenames.append(example_project_dir / 'Makefile')
        for filename in filenames:
            logger.debug(f'cp {filename} to {project_dir}')
            shutil.copy(filename, project_dir)
        (project_dir / 'figs').mkdir()
        logger.info(f'Created and initalized {project_dir}')

    def __init__(self, cwd=Path.cwd(), project_dir=Path.cwd(),
                 debug=False, colour=True, warn_stderr=True):
        assert BasmatiProject._is_project_root_dir(project_dir)

        self.project_dir = project_dir
        self.cwd = cwd
        self.config = None

        debug |= os.getenv('$BASMATI_DEBUG', 'false').lower() == 'true'
        colour |= os.getenv('$BASMATI_COLOUR', 'false').lower() == 'true'
        warn_stderr |= os.getenv('$BASMATI_WARN_STDERR', 'false').lower() == 'true'

        self.logger = setup_logger(debug, colour, warn_stderr)
        self.logging_filename = Path(self.project_dir / self.dotbasmati_dir / 'basmati.log')
        add_file_logging(self.logging_filename)

        self._load_config()

    def __repr__(self):
        return 'BasmatiProject("{}")'.format(self.project_dir)

    def __str__(self):
        return self.__repr__()

    def _load_config(self):
        config_filename = self.project_dir / 'basmati.conf'
        self.config = ConfigParser()
        with open(config_filename, 'r') as f:
            self.config.read_file(f)
        logger.debug('loaded suite config')

        self.hydrosheds_dir = Path(os.path.expandvars(self.config['settings']['hydrosheds_dir']))
