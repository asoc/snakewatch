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

import logging


class UIPrint(object):
    def __init__(self, notice, warning, error):
        self.notice = notice
        self.warning = warning
        self.error = error

ui_print = UIPrint(print, print, print)
config = None

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class SysToLogging(object):
    def __init__(self, log_level):
        self.log_level = log_level
        self.linebuf = ''

    def flush(self):
        pass

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            logging.log(self.log_level, line.rstrip())


class AbortError(Exception):
    def __init__(self):
        super(AbortError, self).__init__()


class ConfigError(Exception):
    '''Raised when a config error has been detected'''

    def __init__(self, message):
        super(ConfigError, self).__init__(message)


class NotConfirmedError(Exception):
    '''Raised when the user has not confirmed a ConfirmAction'''

    def __init__(self):
        super(NotConfirmedError, self).__init__()
