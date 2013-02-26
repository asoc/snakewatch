'''
This file is part of snakewatch.

snakewatch is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

snakewatch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with snakewatch.  If not, see <http://www.gnu.org/licenses/>.
'''

# Future modules
from __future__ import print_function

# System modules
import sys
import signal
import stat
import os
import argparse
import logging
from logging.handlers import RotatingFileHandler

# Program modules
from snakewatch import NAME, VERSION, DESCRIPTION, USER_PATH, \
    LOG_FILE, LOG_LEVEL, LOG_BACKUP_COUNT, LOG_MAX_BYTES, LOG_FORMAT, LOG_TO_STDOUT


_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)

_log_handler = logging.StreamHandler()
_log_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT))
_logger.addHandler(_log_handler)


def get_logger(name):
    '''Get a logging instance consistent with the main logger'''
    return _logger.getChild(name)


from snakewatch.input import File, STD


def main():
    global _log_handler

    log_to_file = True
    if not os.path.exists(USER_PATH):
        try:
            os.makedirs(USER_PATH)
        except OSError:
            log_to_file = False
            print('Unable to create snakewatch settings/log directory.',
                  'Please create the directory %s' % USER_PATH,
                  sep='\n', file=sys.stderr)

    if not os.access(USER_PATH, os.W_OK):
        try:
            mode = stat.S_IWRITE
            if not sys.platform == 'win':
                st = os.stat(USER_PATH)
                mode = mode | st.mode
            os.chmod(USER_PATH, mode)
        except OSError:
            log_to_file = False
            print('Unable to write to snakewatch settings/log directory.',
                  'Please set write permissions to the directory %s' % USER_PATH,
                  sep='\n', file=sys.stderr)

    if log_to_file and not LOG_TO_STDOUT:
        _logger.removeHandler(_log_handler)
        _log_handler.close()

        _log_handler = RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
        )

        _log_handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT))
        _logger.addHandler(_log_handler)
    
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=VERSION
    )
    parser.add_argument(
        '-c', '--config', 
        help='which configuration file to use'
    )
    parser.add_argument(
        '-n', '--lines',
        default=0, type=int,
        help='start LINES from end of the file, use -1 to start at the beginning',
    )

    watch_loc_group = parser.add_mutually_exclusive_group()
    watch_loc_group.add_argument(
        '-w', '--watch', 
        help='which file to watch'
    )
    watch_loc_group.add_argument(
        '-r', '--read',
        action='store_true',
        help='read input from stdin'
    )
    
    args = parser.parse_args(sys.argv[1:])
    
    _logger.debug('%s\n' % ('=' * 40))

    from snakewatch.ui import Console
    handler = Console.ConsoleUI()
    
    if sys.platform.startswith('win'):
        signal.signal(signal.CTRL_C_EVENT, handler.handle_signal)
    else:
        signal.signal(signal.SIGHUP, handler.handle_signal)
        signal.signal(signal.SIGQUIT, handler.handle_signal)
    signal.signal(signal.SIGINT, handler.handle_signal)
    signal.signal(signal.SIGTERM, handler.handle_signal)
    signal.signal(signal.SIGABRT, handler.handle_signal)
    
    if args.read:
        input = STD.STDInput()
    elif args.watch is not None:
        input = File.FileInput(args.watch, args.lines)
    else:
        input = None
    
    try:
        handler.run(input, args.config)
    except:
        import traceback
        exc_type, exc_value = sys.exc_info()[:2]
        exc_traceback = traceback.extract_stack()
        handler.fatal_error(exc_type, exc_value, exc_traceback)

    _logger.debug('snakewatch exiting\n')
    _log_handler.close()

if __name__ == '__main__':
    main()
