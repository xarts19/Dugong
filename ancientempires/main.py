#!/usr/bin/env python

"""Main file.

"""

__author__ = "Xarts19 (xarts19@gmail.com)"
__version__ = "Version: 0.0.1 "
__date__ = "Date: 2011-08-22 12:26:37.904459 "


import sys
import optparse
import logging
from external import colorer
LOGGER = logging.getLogger('main')

LOGGER_FORMAT = "%(name)s--%(levelname)s--%(asctime)s - %(message)s"
LOGGER_DATE_FORMAT = "%d-%m-%y %H:%M:%S"

def init_logging(debug_level):
    '''Initialize logging system.'''
    LOGGER.setLevel(debug_level)
    LOGGER.propagate = 0
    streamLogger = logging.StreamHandler()
    streamLogger.setLevel(debug_level)
    formatter = logging.Formatter(LOGGER_FORMAT, LOGGER_DATE_FORMAT)
    streamLogger.setFormatter(formatter)
    LOGGER.addHandler(streamLogger)


def parse_args():
    '''Parse cli arguments.'''
    parser = optparse.OptionParser(description=__doc__, prog='Ancient Empires',
                        version=__version__)
    parser.add_option('-d', '--debug', action='store_const', dest='debug',
                        const=logging.DEBUG, help='show debug information')
    parser.add_option('-v', '--verbose', action='store_const', dest='debug',
                        const=logging.INFO, help='show additional information')
    opts = parser.parse_args()[0]

    debug_level = logging.WARNING
    if opts.debug:
        debug_level = opts.debug
    init_logging(debug_level)

    LOGGER.debug('cli options: %s', opts)


def main():
    '''Launch the program.'''
    parse_args()
    try:
        import window
        game = window.Window()
        game.run()
        return 0
    except Exception as ex:
        LOGGER.exception('Program exited unexpectedly: ')
        return 1
    except BaseException as ex:
        LOGGER.exception('Program exited unexpectedly: ')
        return 1

if __name__ == "__main__":
    sys.exit(main())
