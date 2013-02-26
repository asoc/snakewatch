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

from __future__ import print_function

import os
import logging
from colorama import init as cl_init, deinit as cl_deinit, Fore, Back, Style

from snakewatch import config
from snakewatch.main import get_logger


_PREPEND_MSG = '\n%(reset)s *** [%(dim)s%(name)s%(reset)s] ' % {
    'reset': Style.RESET_ALL, 'dim': Style.DIM, 
    'name': 'snakewatch.%d' % os.getpid(),
}

_NOTICE_CLR = Fore.GREEN + Style.DIM
_ERROR_CLR = Fore.RED + Style.BRIGHT

_logger = get_logger('Console')


class ConsoleUI(object):
    '''UI Handler that outputs to sys.stdout'''

    def __init__(self, *args):
        self.received_signal = False
        self.interrupted = False
        self.input = None
        self.current_style = Style.RESET_ALL
    
    def run(self, start_input, start_config):
        '''Read in the config and start watching the input'''
        cl_init()
        
        if start_input is None:
            self.print_err(
                'One of \'--watch\' or \'--read\' must be provided.\n' \
                'Use \'--help\' for more information.'
            )
            self.close()
            return
            
        if start_config is None:
            self.cfg = config.DefaultConfig(self)
            msg = 'No config provided, using %s' % self.cfg.source
            if self.cfg.source == 'default':
                msg = '\n'.join([msg, 'Consider creating %s' % config.DefaultConfig.file_for(self)])
            self.print_ntc(msg)
        else:
            try:
                self.cfg = config.Config(start_config)
            except Exception as err:
                self.print_err('Error in config script %s\n%s' % (
                    start_config, err
                ))
                self.close()
                return
        
        self.input = start_input
        self.interrupted = False
        self.input.watch(
            self.started_callback, 
            self.output_callback, 
            self.int_callback
        )

        self.close()

    def fatal_error(self, exc_type, exc_value, exc_traceback):
        '''Called when an unhandled exception is raised from run()'''
        if not isinstance(exc_value, str):
            msg = str(exc_value)
        else:
            msg = exc_value

        from snakewatch import LOG_LEVEL

        if LOG_LEVEL == logging.DEBUG and exc_traceback:
            import traceback
            self.print_err(''.join(traceback.format_list(exc_traceback)).rstrip('\n'))

        self.print_err(': '.join([exc_type.__name__, msg]))

    def started_callback(self):
        '''Called when the watcher has successfully opened the input'''
        if self.interrupted:
            self.print_ntc('Watch resuming on %s' % self.input.name())
        else:
            self.print_ntc('(press Ctrl-C to stop) Watching %s' % 
                self.input.name()
            )
        self.interrupted = False
        
    def output_callback(self, line):
        '''Called when the watcher has read a line and performed an action'''
        self.interrupted = False
        output = self.cfg.match(line)
        if output:
            print(output, end='')
        
    def int_callback(self, error):
        '''Called when the watcher encounters a problem'''
        if not self.interrupted:
            self.print_err('Watch interrupted: %s' % (error))
        self.interrupted = True
        
    def handle_signal(self, signum, frame):
        '''Handle an OS signal from the user'''
        self.received_signal = True

        _logger.debug('Received signal: %d' % signum)
        if self.input:
            self.input.close()
        self.close()
        
    def close(self):
        '''Close any necessary resources'''
        if self.received_signal:
            self.print_err('Received interrupt, quitting')
        
        print(Style.RESET_ALL, end='')
        cl_deinit()
    
    def print_msg(self, msg):
        '''Print a formatted message'''
        try:
            msg = msg.replace('\n', _PREPEND_MSG)
        except AttributeError:
            pass
        print(''.join([_PREPEND_MSG, msg, self.current_style]))
        print()
    
    def print_ntc(self, msg):
        '''Print a formatted notice message'''
        prep = ''.join([
            _PREPEND_MSG,
            (Style.RESET_ALL + _NOTICE_CLR)
        ])
        try:
            msg = msg.replace('\n', prep)
        except AttributeError:
            pass
        print(''.join([prep, msg, self.current_style]))
        print()
    
    def print_err(self, msg):
        '''Print a formatted error message'''
        prep = ''.join([
            _PREPEND_MSG, 
            (Style.RESET_ALL + _ERROR_CLR)
        ])
        try:
            msg = msg.replace('\n', prep)
        except AttributeError:
            pass
        print(''.join([prep, msg, self.current_style]))
        print()
