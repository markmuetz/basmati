import logging
import os
import sys
from typing import Union

from basmati.bcolors import Bcolors


# Thanks: # http://stackoverflow.com/a/8349076/54557
class ColourConsoleFormatter(logging.Formatter):
    """Format messages in colour based on their level"""
    dbg_fmt = '%(asctime)s: ' +  Bcolors.OKBLUE + '%(levelname)-8s' + Bcolors.ENDC + ': %(message)s'
    info_fmt = '%(asctime)s: ' + Bcolors.OKGREEN + '%(levelname)-8s' + Bcolors.ENDC + ': %(message)s'
    file_fmt = '%(asctime)s: ' + Bcolors.HEADER + '%(levelname)-8s' + Bcolors.ENDC + ': %(message)s'
    warn_fmt = '%(asctime)s: ' + Bcolors.WARNING + '%(levelname)-8s' + Bcolors.ENDC + ': %(message)s'
    err_fmt = ('%(asctime)s: ' + Bcolors.FAIL + '%(levelname)-8s' + Bcolors.ENDC +
               Bcolors.BOLD + ': %(message)s' + Bcolors.ENDC)
 
    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt, '%H:%M:%S')
 
    def format(self, record):
        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = ColourConsoleFormatter.dbg_fmt
        elif record.levelno == logging.INFO:
            self._fmt = ColourConsoleFormatter.info_fmt
        elif record.levelno == logging.WARNING:
            self._fmt = ColourConsoleFormatter.warn_fmt
        elif record.levelno == logging.ERROR:
            self._fmt = ColourConsoleFormatter.err_fmt

        if hasattr(self, '_style'):
            self._style._fmt = self._fmt
 
        # Call the base formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
 
        return result
 
 
def add_file_logging(logging_filename: str) -> None:
    """Add file logging to basmati logger.

    Idempotent.

    :param logging_filename: file to output logging to.
    """
    basmati_logger = logging.getLogger('basmati')

    if getattr(basmati_logger, 'has_file_logging', False):
        # Stops log being setup for a 2nd time during ipython reload(...)
        basmati_logger.debug('Root logger already has file logging')
    else:
        basmati_logger.debug(f'Adding file handler {logging_filename}')
        file_formatter = logging.Formatter('%(asctime)s:%(name)-20s:%(levelname)-8s: %(message)s')
        fileHandler = logging.FileHandler(logging_filename, mode='a')
        fileHandler.setFormatter(file_formatter)
        fileHandler.setLevel(logging.DEBUG)

        basmati_logger.addHandler(fileHandler)


def setup_logger(level: Union[str, int] = logging.INFO,
                 colour: bool = True, warn_stderr: bool = False) -> logging.Logger:
    """Configure a basmati logger.

    Only do once (i.e. can call repeatedly and it will not change - idempotent).
    Uses only a StreamHandler - only logs to console.

    :param level: logging level
    :param colour: use colour logs in console output
    :param warn_stderr: warn and higher in stderr
    :return: configured basmati logger
    """
    '''Gets a logger. Sets up root logger ('basmati') if nec.'''
    basmati_logger = logging.getLogger('basmati')

    if getattr(basmati_logger, 'is_setup', False):
        # Stops log being setup for a 2nd time during ipython reload(...)
        basmati_logger.debug('Root logger already setup')
    else:
        fmt = '%(asctime)s: %(levelname)-8s: %(message)s'
        if not colour:
            console_formatter = logging.Formatter(fmt)
        else:
            console_formatter = ColourConsoleFormatter(fmt)

        if isinstance(level, str):
            loglevel: int = getattr(logging, level)
        envlevel = os.getenv('BASMATI_LOGLEVEL', None)
        if envlevel:
            envloglevel = getattr(logging, envlevel)
            loglevel = min(envloglevel, loglevel)

        basmati_logger.setLevel(loglevel)

        stdoutStreamHandler = logging.StreamHandler(sys.stdout)
        stdoutStreamHandler.setFormatter(console_formatter)
        basmati_logger.addHandler(stdoutStreamHandler)

        if warn_stderr:
            stderrStreamHandler = logging.StreamHandler(sys.stderr)
            stderrStreamHandler.setFormatter(logging.Formatter(fmt))
            stderrStreamHandler.setLevel(logging.WARNING)
            basmati_logger.addHandler(stderrStreamHandler)

        setattr(basmati_logger, 'is_setup', True)

    return basmati_logger
