import sys
import signal
from colorama import init as cl_init, deinit as cl_deinit, Fore, Back, Style

from UIHandler import UIHandler
from snakewatch import NAME

_PREPEND_MSG = '\n%(reset)s *** [%(dim)s%(name)s%(reset)s] ' % {
    'reset': Style.RESET_ALL, 'dim': Style.DIM, 
    'name': NAME,
}

def sw_print(msg):
    try:
        msg = msg.replace('\n', _PREPEND_MSG)
    except AttributeError:
        pass
    print '%s%s' % (_PREPEND_MSG, msg)

def quit(msg=None, errmsg=None):
    code = 0
    if errmsg is not None:
        sw_print('%s%s' % (Style.RESET_ALL + Fore.RED + Style.BRIGHT, errmsg))
        code = 1
    if msg is not None:
        sw_print(msg)
        
    cl_deinit()
    sys.exit(code)

class ConsoleHandler(UIHandler):
    received_interrupt = False
    
    def __init__(self, *args):
        super(ConsoleHandler, self).__init__(args)
        
    def run(self, start_input, start_config):
        cl_init()
        while True:
            pass
    
    def close(self):
        pass
    
    def handle_signal(self, signum, frame):
        quit(errmsg='Received interrupt, quitting')