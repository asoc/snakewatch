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

import re
from abc import ABCMeta, abstractmethod, abstractproperty

class Action(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, cfg):
        self.cfg = cfg
    
    def matches(self, line):
        if re.match(self.cfg['regex'], line):
            return True
        return False
    
    @abstractmethod
    def run_on(self, line):
        print ''