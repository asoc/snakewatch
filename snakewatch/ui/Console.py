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

import os
import sys
import signal
from colorama import init as cl_init, deinit as cl_deinit, Fore, Back, Style

from snakewatch import config

_PREPEND_MSG = '\n%(reset)s *** [%(dim)s%(name)s%(reset)s] ' % {
    'reset': Style.RESET_ALL, 'dim': Style.DIM, 
    'name': 'snakewatch',
}

_NOTICE_CLR = Fore.GREEN + Style.DIM

class ConsoleUI():
    def __init__(self, *args):
        self.received_interrupt = False
        self.watching = False
        self.input = None
        self.current_style = Style.RESET_ALL
    
    def run(self, start_input, start_config):
        cl_init()
        
        if start_input is None:
            self.print_err(
                'One of \'--watch\' or \'--read\' must be provided when ' \
                '\'--console\' is enabled.\n' \
                'Use \'--help\' for more information.'
            )
            self.quit()
            
        if start_config is None:
            self.cfg = config.DefaultConfig()
            self.print_ntc('No config provided, using default')
        else:
            try:
                self.cfg = config.Config(start_config)
            except Exception as err:
                self.print_err('Error in config script %s\n%s' % (
                    start_config, err
                ))
                self.quit()
        
        self.input = start_input
        self.watching = True
        self.input.watch(
            self.started_callback, 
            self.output_callback, 
            self.int_callback
        )
        
    def started_callback(self):
        if not self.watching:
            self.print_ntc('Watch resuming on %s' % self.input.name())
        else:
            self.print_ntc('(press Ctrl-C to stop) Watching %s' % 
                self.input.name()
            )
        
    def output_callback(self, line):
        self.watching = True
        output = self.cfg.match(line)
        if output:
            print output,
        
    def int_callback(self, error):
        if self.watching:
            self.print_err('Watch interrupted: %s' % (error))
        self.watching = False
        
    def handle_signal(self, signum, frame):
        self.received_interrupt = True
        if not self.watching:
            self.quit()
        else:
            self.input.close()
        
    def quit(self):
        if self.received_interrupt:
            self.print_err('Received interrupt, quitting')
        
        print Style.RESET_ALL,
        cl_deinit()
        sys.exit()
    
    def print_msg(self, msg):
        try:
            msg = msg.replace('\n', _PREPEND_MSG)
        except AttributeError:
            pass
        print '%s%s%s' % (_PREPEND_MSG, msg, self.current_style)
        print ''
    
    def print_ntc(self, msg):
        try:
            msg = msg.replace('\n', _PREPEND_MSG)
        except AttributeError:
            pass
        print '%s%s%s%s' % (_PREPEND_MSG, _NOTICE_CLR, msg, self.current_style)
        print ''
    
    def print_err(self, msg):
        prep = '%s%s' % (
            _PREPEND_MSG, 
            (Style.RESET_ALL + Fore.RED + Style.BRIGHT)
        )
        try:
            msg = msg.replace('\n', prep)
        except AttributeError:
            pass
        print '%s%s%s' % (prep, msg, self.current_style)
        print ''
        
