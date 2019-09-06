from pathlib import Path
from configparser import ConfigParser
from logging import getLogger

import basmati
from basmati.basmati_errors import BasmatiError

logger = getLogger('basmati.bm_project')


class BasmatiProject:
    dotbasmati_dir = '.basmati'

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

    def __init__(self, cwd=Path.cwd(), project_dir=Path.cwd()):
        assert BasmatiProject._is_project_root_dir(project_dir)
        self.project_dir = project_dir
        self.cwd = cwd
        self.config = None
        self.logging_filename = ''

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

        self.hydrosheds_dir = Path(self.config['settings']['hydrosheds_dir'])
