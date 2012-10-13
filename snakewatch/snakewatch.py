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
    signal.signal(signal.SIGABRT, handler.handle_signal)
    
    if args.read:
        input = sys.stdin
    else:
        input = args.watch
    
    handler.run(input, args.config)
    

if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit()
