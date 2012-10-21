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

class Input():
    __metaclass__ = ABCMeta
    
    def connect_process(self, pipe):
        self.pipe = pipe
        
    def process_pipe(self):
        if self.pipe is not None:
            signal = None
            try:
                if self.pipe.poll():
                    signal = self.pipe.recv()
            except Exception:
                pass
            if signal == 'close':
                self.close()
    
    @abstractproperty
    def name(self):
        return None
    
    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def watch(self, started_callback, output_callback, int_callback):
        pass
    
    @abstractmethod
    def close(self):
        pass