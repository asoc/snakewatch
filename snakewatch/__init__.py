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
VERSION = '1.0.0.rc-1'
DESCRIPTION = '%s v%s\nA log watcher' % (NAME, VERSION)
URL = 'http://illogi.ca/l/projects/snakewatch'
AUTHOR = 'Alex Honeywell'
AUTHOR_EMAIL = 'alex.honeywell@gmail.com'

USER_PATH = os.path.expanduser(os.path.join('~', '.snakewatch'))

LOG_FILE = os.path.join(USER_PATH, 'snakewatch.log')
LOG_TO_STDOUT = False
LOG_FORMAT = '%(asctime)-15s [%(levelname)s] %(name)s: %(message)s'
LOG_LEVEL = logging.INFO
LOG_MAX_BYTES = 1024*1024*5
LOG_BACKUP_COUNT = 1

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
