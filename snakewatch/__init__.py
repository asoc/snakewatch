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
import logging

NAME = 'snakewatch'
VERSION = '0.1.dev-1'
DESCRIPTION = '%s v%s\nA log watcher' % (NAME, VERSION)
URL = 'http://bitbucket.org/asoc/snakewatch'
AUTHOR = 'Alex Honeywell',
AUTHOR_EMAIL = 'alex.honeywell@gmail.com',

USER_PATH = os.path.expanduser(os.path.join('~', '.snakewatch'))

LOG_FILE = os.path.join(USER_PATH, 'snakewatch.log')
LOG_FORMAT = '%(asctime)-15s [%(levelname)s] %(module)s.%(lineno)d.%(funcName)s: %(message)s'
LOG_LEVEL = logging.DEBUG

#_stat = os.stat(LOG_FILE)
#if _stat.st_size > 256000:
#    _rollover = '%s.1' % LOG_FILE
#    if os.path.exists(_rollover):
#        os.unlink(_rollover)
#    os.rename(LOG_FILE, _rollover)

logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)

class SysToLogging(object):
    def __init__(self, log_level):
        self.log_level = log_level
        self.linebuf = ''
        
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            logging.log(self.log_level, line.rstrip())