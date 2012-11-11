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
import copy
from abc import ABCMeta, abstractmethod, abstractproperty

class Action(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, cfg):
        self.raw_cfg = copy.deepcopy(cfg)
        self.cfg = cfg
        self.pattern = re.compile(self.cfg['regex'])
        self.name = self.__module__.split('.')[-1:][0]
    
    def matches(self, line):
        return self.pattern.match(line) is not None
    
    @abstractmethod
    def run_on(self, line):
        print ''