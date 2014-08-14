"""
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
"""

from __future__ import print_function

import os
import re
import logging
from colorama import init as cl_init, deinit as cl_deinit, Fore, Back, Style

import snakewatch.util
from snakewatch import config
from snakewatch.mode import get_arg_group, add_cmdln_argument
from snakewatch.util import UIPrint, AbortError, get_read_object
from snakewatch.main import get_logger, parser
from snakewatch.cursescmd import cursescmd

# Force no curses, just use the Cmd extensions
cursescmd.curses = None

_PREPEND_MSG = '\n%(reset)s *** [%(dim)s%(name)s%(reset)s] ' % {
    'reset': Style.RESET_ALL, 'dim': Style.DIM, 
    'name': 'snakewatch.%d' % os.getpid(),
}

_NOTICE_CLR = Fore.GREEN + Style.DIM
_WARNING_CLR = Fore.YELLOW + Style.BRIGHT
_ERROR_CLR = Fore.RED + Style.BRIGHT

_logger = get_logger('Console')


def setup_arguments(argparser):
    pass
    # group = get_arg_group(argparser, 'Console')
    # add_cmdln_argument(
    #     group, 'Console',
    #     '-i', '--interactive',
    #     action='store_true',
    #     help='run in interactive mode'
    # )
    # add_cmdln_argument(
    #     group, 'Console',
    #     '-r', '--auto-run',
    #     action='store_true',
    #     help='start watching right away'
    # )


class Interactive(cursescmd.CmdBase):
    def __init__(self, console, args):
        super(Interactive, self).__init__()

        self.console = console
        self.args = args
        self.prompt = 'SW > '
        self.canceled = False

        self.set_arg_parser('setargs', parser)

    def do_setargs(self, args):
        if args:
            self.args = args

    def do_setwatch(self, query):
        if not query:
            self.console.print_err('Watch location must be provided (stdin cannot be used in interactive mode)')
            return

        path = os.path.abspath(query)
        if not os.path.exists(path):
            self.console.print_err('{} does not exist'.format(path))
            return

        if not os.access(path, os.R_OK):
            self.console.print_err('{} is not readable'.format(path))
            return

        self.args.watch = path

    def do_setconfig(self, query):
        if not query:
            self.console.print_err('Config location must be provided.')
            return

        self.args.config = config.find_config(query)

    def do_run(self, query=''):
        self.console.run(get_read_object(self.args), self.args, from_interactive=True)

    def cmdloop(self, intro=None):
        if self.args.console_auto_run:
            self.do_run()
        cursescmd.CmdBase.cmdloop(self, intro)


class ConsoleMode(object):
    """UI Handler that outputs to sys.stdout"""

    def __init__(self, *args):
        self.closed = False
        self.cfg = None
        self.received_signal = False
        self.interrupted = False
        self.input = None
        self._waiting_for_input = None
        self.current_style = Style.RESET_ALL
        self.interactive = None
        self.watch_loc = None
        self.config_loc = None

        snakewatch.util.ui_print = UIPrint(self.print_ntc, self.print_warn, self.print_err, self.get_choice)

    def run(self, start_input, args, from_interactive=False):
        """Read in the config and start watching the input"""
        cl_init()

        # if not from_interactive and args.console_interactive:
        #     self.interactive = cursescmd.Cmdr(Interactive(self, args))
        #     self.interactive.cmdloop('Snakewatch Interactive Mode')
        #     return

        if not start_input and not self.watch_loc:
            self.print_err(
                'One of \'--watch\' or \'--read\' must be provided.\n' \
                'Use \'--help\' for more information.'
            )
            self.close()
            return

        self.watch_loc = start_input or self.watch_loc

        ui_kwargs = {'ui_confirm': self.confirm}
        if not args.config and not self.config_loc:
            if args.no_config:
                self.cfg = config.DefaultConfig(self, use_file=False, ui_kwargs=ui_kwargs)
            else:
                self.cfg = config.DefaultConfig(self, ui_kwargs=ui_kwargs)
                msg = 'No config provided, using %s' % self.cfg.source
                if self.cfg.source == 'default':
                    msg = '\n'.join([msg, 'Consider creating %s' % config.DefaultConfig.file_for(self)])
                self.print_ntc(msg)
        else:
            try:
                self.cfg = config.Config(args.config or self.config_loc, ui_kwargs)
            except AbortError:
                self.close()
                return
            except Exception as err:
                self.print_err('Error in config script %s\n%s' % (
                    args.config, err
                ))
                self.close()
                return

        self.config_loc = self.cfg.source
        
        self.input = start_input
        self.interrupted = False
        self.input.watch(
            self.started_callback, 
            self.output_callback, 
            self.int_callback
        )

        self.close()

    def confirm(self, msg):
        self.print_warn(msg)
        response = 'n'
        prompt = 'Is this OK? [Y/N] : '
        while prompt and not self.received_signal:
            self._waiting_for_input = True
            try:
                response = raw_input(prompt).lower()
            except EOFError:
                return False
            finally:
                self._waiting_for_input = False

            if response:
                response = response[0]
            prompt = 'Please enter Y or N: ' if response not in ['y', 'n'] else None
        return response == 'y'

    def fatal_error(self, exc_type, exc_value, exc_traceback):
        """Called when an unhandled exception is raised from run()"""
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
        """Called when the watcher has successfully opened the input"""
        if self.interrupted:
            self.print_ntc('Watch resuming on %s' % self.input.name())
        else:
            self.print_ntc('(press Ctrl-C to stop) Watching %s' % self.input.name())
        self.interrupted = False
        
    def output_callback(self, line):
        """Called when the watcher has read a line and performed an action"""
        self.interrupted = False
        self.cfg.match(line, print, **{'end': ''})

    def int_callback(self, error):
        """Called when the watcher encounters a problem"""
        if not self.interrupted:
            self.print_err('Watch interrupted: %s' % error)
        self.interrupted = True
        
    def handle_signal(self, signum, frame):
        """Handle an OS signal from the user"""
        self.received_signal = True

        if self._waiting_for_input:
            self.print_err('Waiting for stdin data. Press enter to quit (use Ctrl/Cmd-D to avoid this message)')
            return

        _logger.debug('Received signal: %d' % signum)
        if self.input:
            self.input.close()

        self.close()
        
    def close(self):
        """Close any necessary resources"""
        if self.closed:
            return

        self.closed = True
        if self.interactive and not self.input:
            self.interactive.cancel()
        elif self.received_signal:
            self.print_err('Received interrupt, {}'.format('stopping' if self.interactive else 'quitting'))
        
        print(Style.RESET_ALL, end='')
        cl_deinit()

        if self.interactive:
            interactive = self.interactive
            self.__init__()
            self.interactive = interactive

    def get_choice(self, message, prompt, choices, **kwargs):
        self.print_warn(*(message,), **kwargs)
        _choices = []
        choice_range = range(1, len(choices) + 1)
        for i in choice_range:
            _choices.append('{:>2d} - {}'.format(i, choices[i-1]))
        self.print_ntc(*_choices)

        choice = None
        _prompt = prompt
        _colour = _NOTICE_CLR
        while not choice:
            try:
                _choice = raw_input('{}{}: {}'.format(_colour, _prompt, Style.RESET_ALL))
            except EOFError:
                print()
                return None
            _choice = map(int, re.findall(r'\d+', _choice))[0]
            if _choice not in choice_range:
                _prompt = 'Invalid choice, try again'
                _colour = _ERROR_CLR
                continue
            choice = _choice
        return choices[choice-1]

    def print_msg(self, *args, **kwargs):
        """Print a formatted message"""
        self._print(*args, **kwargs)

    def print_warn(self, *args, **kwargs):
        """Print a formatted warning message"""
        self._print(_WARNING_CLR, *args, **kwargs)

    def print_ntc(self, *args, **kwargs):
        """Print a formatted notice message"""
        self._print(_NOTICE_CLR, *args, **kwargs)
    
    def print_err(self, *args, **kwargs):
        """Print a formatted error message"""
        self._print(_ERROR_CLR, *args, **kwargs)

    def _print(self, colour='', *args, **kwargs):
        try:
            sep = kwargs['sep']
        except KeyError:
            sep = '\n'
        prepend = ''.join([_PREPEND_MSG, colour])
        msg = sep.join(args)
        msg = msg.replace('\n', prepend)
        print(''.join([prepend, msg, self.current_style]))
        print()
