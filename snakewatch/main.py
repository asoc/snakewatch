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

# System modules
import sys
import signal
import os
import argparse
import logging

# Program modules
from snakewatch import config, NAME, VERSION, DESCRIPTION
from snakewatch.input import File, STD
from snakewatch.ui import Console, Qt

def get_handler(console):
    if not console:
        try:
            import PySide
        except ImportError:
            print sys.stderr, 'Unable to load PySide library. Please ensure' \
                              ' it is installed and on your PYTHONPATH or' \
                              ' run snakewatch in console mode.'
            sys.exit(1)
        
        return Qt.QtUI()
        
    return Console.ConsoleUI()

def main():
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
        '-o', '--console',
        action='store_true',
        help='don\'t launch a GUI, output to stdout'
    )
    parser.add_argument(
        '-c', '--config', 
        help='which configuration file to use'
    )
    parser.add_argument(
        '-n', '--lines',
        default=0, type=int,
        help='start LINES from end of the file, ' \
             'use -1 to start at the beginning',
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
    
    logging.debug('%s\n' % ('=' * 40))
    handler = get_handler(args.console)
    
    if not sys.platform.startswith('win'): 
        signal.signal(signal.SIGHUP, handler.handle_signal)
        signal.signal(signal.SIGQUIT, handler.handle_signal)
    else:
        signal.signal(signal.CTRL_C_EVENT, handler.handle_signal)
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
    except Exception as err:
        if not args.console:
            logging.exception('Fatal Exception Occurred')
        else:
            import traceback
            traceback.print_exc()
        
    File.FileInput.close_all()
    logging.debug('snakewatch exiting\n')

if __name__ == '__main__':
    main()
