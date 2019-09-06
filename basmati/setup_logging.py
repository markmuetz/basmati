import logging
import sys

from basmati.bcolors import bcolors


# class BraceMessage:
#     def __init__(self, msg, *args, **kwargs):
#         self.msg = str(msg)
#         self.args = args
#         self.kwargs = kwargs
# 
#     def __str__(self):
#         return self.msg.format(*self.args, **self.kwargs)
# 
# 
# class BraceFormatter(logging.Formatter):
#     """Allow deferred formatting of msg using {msg} syntax"""
#     def format(self, record):
#         # record.msg is whatever was passed into e.g. logger.debug(...).
#         # record.args is:
#         #     extra args, or:
#         # kwargs dict:.
#         record_args_orig = record.args
#         record_msg_orig = record.msg
#         # replace record.msg with a BraceMessage and set record.args to ()
#         if isinstance(record.args, dict):
#             args = (record.args,)
#         else:
#             args = record.args
#         kwargs = {}
#         record.args = ()
#         # N.B. msg has not been formatted yet. It will get formatted when
#         # str(...) gets called on the BraceMessage.
#         record.msg = BraceMessage(record.msg, *args, **kwargs)
#         result = logging.Formatter.format(self, record)
# 
#         # Leave everything as we found it.
#         record.args = record_args_orig
#         record.msg = record_msg_orig
# 
#         return result
# 

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
 
        # Call the BraceFormatter formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
 
        return result
 
 
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
        # fmt = '{levelname:8s}: {message}'
        if colour:
            console_formatter = ColourConsoleFormatter(fmt)
            # console_formatter = logging.Formatter(fmt)
        else:
            # console_formatter = BraceFormatter(fmt, style='{')
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
