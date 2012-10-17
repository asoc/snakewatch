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

from abc import ABCMeta, abstractmethod, abstractproperty

from snakewatch.input import File

__AF_ERR = 'Abstract UIHandler functions cannot be called directly.'

class UI(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, *args):
        pass
    
    @abstractmethod
    def run(self, start_input, start_config):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def handle_signal(self, signum, frame):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def started_callback(self):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def output_callback(self, line):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def int_callback(self, error):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def quit(self):
        for fp in File.FileInput.open_files:
            fp.close()
