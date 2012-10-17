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

from _UI import UI

class QtUI(UI):
    def __init__(self, *args):
        super(QtUI, self).__init__(args)
        
    def run(self, start_input, start_config):
        pass

    def handle_signal(self, signum, frame):
        pass
    
    def started_callback(self):
        pass
    
    def output_callback(self, line):
        pass
    
    def int_callback(self, error):
        pass
    
    def quit(self):
        super(QtHandler, self).quit()