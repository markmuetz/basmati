"""Entry point into running basmati from command line

all commands are run as:
    basmati [basmati_opts] <cmd> [cmd_opts] [cmd_args]
"""
import os
from pathlib import Path

import basmati
import basmati.cmds as cmds
from basmati.cmds.cmd_context import CmdContext
from basmati.command_parser import parse_commands
from basmati.setup_logging import setup_logger
from basmati.basmati_project import BasmatiProject
from basmati.basmati_errors import BasmatiError

# Top level args, e.g. basmati -D ...
ARGS = [(['--throw-exceptions', '-X'], {'action': 'store_true', 'default': False}),
        (['--DEBUG', '-D'], {'action': 'store_true', 'default': False}),
        (['--bw-logs', '-b'], {'action': 'store_true', 'default': False})]


def main(argv, import_log_msg=''):
    "Parse commands/env, setup logging, dispatch to cmds/<cmd>.py"
    basmati_cmds, args = parse_commands('basmati', ARGS, cmds, argv[1:])
    cmd = basmati_cmds[args.cmd_name]

    env_debug = os.getenv('BASMATI_DEBUG') == 'True'

    if args.DEBUG or env_debug:
        debug = True
    else:
        debug = False

    colour = not args.bw_logs
    warn_stderr = False
    logger = setup_logger(debug, colour, warn_stderr)

    project_dir = BasmatiProject.basmati_project_dir(Path.cwd())
    if project_dir:
        project = BasmatiProject(Path.cwd(), project_dir)
    else:
        if not getattr(cmd, 'RUN_OUTSIDE_PROJECT', False):
            logger.error('Not in a basmati project')
            return
        project = None

    logger.debug(f'start dir: {Path.cwd()}')
    logger.debug(f'basmati import: {import_log_msg}')
    logger.debug(' '.join(argv))
    logger.debug(args)
    logger.debug(args.cmd_name)

    cmd_ctx = CmdContext(project)
    if not args.throw_exceptions:
        logger.debug('Catching all exceptions')
        try:
            # dispatch on arg
            return cmd.main(cmd_ctx, args)
        except BasmatiError as be:
            logger.error(f'{be}')
        except Exception as e:
            logger.exception(f'{e}')
            if debug:
                import ipdb
                ipdb.post_mortem()
            raise
    else:
        return cmd.main(cmd_ctx, args)
