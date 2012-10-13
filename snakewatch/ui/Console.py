import sys
import signal
from colorama import init as cl_init, deinit as cl_deinit, Fore, Back, Style

from UIHandler import UIHandler
from snakewatch import NAME
import input_type

_PREPEND_MSG = '\n%(reset)s *** [%(dim)s%(name)s%(reset)s] ' % {
    'reset': Style.RESET_ALL, 'dim': Style.DIM, 
    'name': NAME,
}

class ConsoleHandler(UIHandler):
    def __init__(self, *args):
        super(ConsoleHandler, self).__init__(args)
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
        
        self.input = start_input
        self.watching = True
        self.input.watch(self.started_callback, self.output_callback, self.int_callback)

    def started_callback(self):
        if not self.watching:
            self.print_msg('%sWatch resuming on %s' % (Fore.GREEN + Style.DIM, self.input.name()))
        else:
            self.print_msg('%sWatching %s' % (Fore.GREEN + Style.DIM, self.input.name()))
        
    def output_callback(self, line):
        self.watching = True
        print self.match_config_entry(line),
        
    def int_callback(self, error):
        if self.watching:
            self.print_err('Watch interrupted: %s' % (error))
        self.watching = False
        
    def match_config_entry(self, line):
        return line
    
    def handle_signal(self, signum, frame):
        self.received_interrupt = True
        if not self.watching:
            self.quit()
        else:
            self.input.close()
        
    def quit(self):
        if self.received_interrupt:
            self.print_err('Received interrupt, quitting')

        super(ConsoleHandler, self).quit()
        cl_deinit()
        sys.exit()
        
    def print_msg(self, msg):
        try:
            msg = msg.replace('\n', _PREPEND_MSG)
        except AttributeError:
            pass
        print '%s%s%s' % (_PREPEND_MSG, msg, self.current_style)
        print ''
    
    def print_err(self, msg):
        prep = '%s%s' % (_PREPEND_MSG, (Style.RESET_ALL + Fore.RED + Style.BRIGHT))
        try:
            msg = msg.replace('\n', prep)
        except AttributeError:
            pass
        print '%s%s%s' % (prep, msg, self.current_style)
        print ''
        