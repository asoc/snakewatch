'''
Python Tail'er
'''
#!/usr/bin/env python

# System modules
import sys
import signal
import os
import argparse

# Program modules
import ui
import config
from input import File, STD

NAME = 'snakewatch'
VERSION = '0.1.dev'
DESCRIPTION = '%s v%s\nA log watcher' % (NAME, VERSION)

def main(args):
    '''
    Main code entry point
    '''
    
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
    
    args = parser.parse_args(args)
    
    handler = ui.get_handler(args.console)
    
    signal.signal(signal.SIGHUP, handler.handle_signal)
    signal.signal(signal.SIGINT, handler.handle_signal)
    signal.signal(signal.SIGQUIT, handler.handle_signal)
    signal.signal(signal.SIGTERM, handler.handle_signal)
    
    if args.read:
        input = STD.STDInput()
    elif args.watch is not None:
        input = File.FileInput(args.watch, args.lines)
    else:
        input = None
    
    handler.run(input, args.config)
    handler.quit()

if __name__ == '__main__':
    main(sys.argv[1:])
