import importlib
from collections import OrderedDict
from logging import getLogger

logger = getLogger('basmati.cmds')

commands = [
    'download',
    'init',
    'shell',
    'version',
]

modules = OrderedDict()
for command in commands:
    command_name = 'cmds.' + command.replace('-', '_')
    try:
        modules[command] = importlib.import_module('basmati.' + command_name)
    except ImportError as e:
        logger.warning('Cannot load module {}'.format(command_name))
        logger.warning(e)
