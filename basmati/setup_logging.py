import logging
import sys

from basmati.bcolors import bcolors


# Thanks: # http://stackoverflow.com/a/8349076/54557
class ColourConsoleFormatter(logging.Formatter):
    '''Format messages in colour based on their level'''
    dbg_fmt = bcolors.OKBLUE + '%(levelname)-8s' + bcolors.ENDC + ': %(message)s'
    info_fmt = bcolors.OKGREEN + '%(levelname)-8s' + bcolors.ENDC + ': %(message)s'
    file_fmt = bcolors.HEADER + '%(levelname)-8s' + bcolors.ENDC + ': %(message)s'
    warn_fmt = bcolors.WARNING + '%(levelname)-8s' + bcolors.ENDC + ': %(message)s'
    err_fmt = (bcolors.FAIL + '%(levelname)-8s' + bcolors.ENDC + bcolors.BOLD + ': %(message)s' + bcolors.ENDC)
 
    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)
 
    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt
 
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
 
 
def add_file_logging(logging_filename, root=True):
    root_logger = logging.getLogger()

    if root and getattr(root_logger, 'has_file_logging', False):
        # Stops log being setup for a 2nd time during ipython reload(...)
        root_logger.debug('Root logger already has file logging')
    else:
        root_logger.debug(f'Adding file handler {logging_filename}')
        file_formatter = logging.Formatter('%(asctime)s:%(name)-20s:%(levelname)-8s: %(message)s')
        fileHandler = logging.FileHandler(logging_filename, mode='a')
        fileHandler.setFormatter(file_formatter)
        fileHandler.setLevel(logging.DEBUG)

        root_logger.addHandler(fileHandler)
        if root:
            root_logger.has_file_logging = True


def setup_logger(debug=False, colour=True, warn_stderr=False):
    '''Gets a logger. Sets up root logger ('basmati') if nec.'''
    root_logger = logging.getLogger()
    basmati_logger = logging.getLogger('basmati')
    root_logger.propagate = False

    root_handlers = []
    while root_logger.handlers:
        # By default, the root logger has a stream handler attached.
        # Remove it. N.B any code that uses basmati should know this!
        root_handlers.append(root_logger.handlers.pop())

    if getattr(basmati_logger, 'is_setup', False):
        # Stops log being setup for a 2nd time during ipython reload(...)
        basmati_logger.debug('Root logger already setup')
    else:
        fmt = '%(levelname)-8s: %(message)s'
        if colour:
            console_formatter = ColourConsoleFormatter(fmt)
        else:
            console_formatter = logging.Formatter(fmt)

        if debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        stdoutStreamHandler = logging.StreamHandler(sys.stdout)
        stdoutStreamHandler.setFormatter(console_formatter)
        stdoutStreamHandler.setLevel(level)

        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(stdoutStreamHandler)

        if warn_stderr:
            stderrStreamHandler = logging.StreamHandler(sys.stderr)
            stderrStreamHandler.setFormatter(logging.Formatter(fmt))
            stderrStreamHandler.setLevel(logging.WARNING)
            root_logger.addHandler(stderrStreamHandler)

        root_logger.is_setup = True

    for hdlr in root_handlers:
        basmati_logger.debug('Removed root handler: {}', hdlr)

    return basmati_logger
