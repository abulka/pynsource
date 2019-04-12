"""
INFO - (and higher) will output to console
DEBUG - will output to console and file

On production DEBUG will
"""

import logging
from app import settings
import os


def log_info(log):
    """
    Utility method which checks if the effective level is what you think it is.

    Args:
        log: an instantiated log object e.g.

            log = logging.getLogger(__name__)
            config_log(log)   # optional
            log_info(log)

    Returns: -

    """
    print(f'log for module name "{__name__}" is {log} with effective level {logging.getLevelName(log.getEffectiveLevel())} ' \
      f'Is it enabled for {logging.getLevelName(logging.DEBUG)} : {log.isEnabledFor(logging.DEBUG)}')




try:
    os.remove(settings.LOG_FILENAME)
except:
    pass

def config_log(log):
    # return turn_off_logging(log)

    # print('log is for debug?', log.isEnabledFor(logging.DEBUG), logging.getLevelName(log.getEffectiveLevel()))
    # print('effective log level', logging.getLogger().getEffectiveLevel())
    # print('effective log level of log', log.getEffectiveLevel())
    log.setLevel(logging.DEBUG)  # starts at WARNING level, so switch it to DEBUG
    # print('effective log level', logging.getLogger().getEffectiveLevel())
    # print('effective log level of log', log.getEffectiveLevel())
    # print('log is for debug?', log.isEnabledFor(logging.DEBUG), logging.getLevelName(log.getEffectiveLevel()))

    # formatter = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')
    # formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    # formatter = logging.Formatter('%(name)s - %(lineno)s - %(message)s')
    # formatter = logging.Formatter('%(asctime)-15s %(levelname)s %(name)s - %(lineno)s - %(message)s')
    # formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(lineno)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(lineno)s - %(message)s', datefmt="%a %I:%S %p")
    # formatter = logging.Formatter('%(name)10s %(message)s')
    # formatter = logging.Formatter('%(message)s')
    # formatter = logging.Formatter('%(levelname)s - %(message)s')

    # create the logging file handler, use append to keep adding to file
    fh = logging.FileHandler(settings.LOG_FILENAME, 'a',
                             'utf-8')  # force to utf08 because python assumes the system default which on windows is sometimes something old and dumb like cp1252
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # create console logging
    if settings.LOG_TO_CONSOLE:
        ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)
        ch.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('PYNSOURCE STREAM %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('PYNSOURCE %(message)s')
        ch.setFormatter(formatter)

    # add them all
    log.addHandler(fh)  # add handler to logger object
    if settings.LOG_TO_CONSOLE:
        log.addHandler(ch)  # add handler to logger object

    # log.propagate = False  # hack to avoid messages getting to root handler, which has a spurious stream handler attached due to importing escpos

    # Removes the spurious stream handler attached to the root logger due to importing escpos
    logging.getLogger('').handlers = [
        h for h in logging.getLogger('').handlers if not isinstance(h, logging.StreamHandler)]

    # log_info(log)  # optional diagnostic


def turn_off_logging(log):
    noop = logging.NullHandler()
    log.addHandler(noop)
