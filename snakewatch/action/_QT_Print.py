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

import cgi
import re

from snakewatch.action._Action import Action

class PrintAction(Action):
    non_alnum = re.compile('[\W_]+')
    hex_colour = re.compile('^(?:[0-9a-fA-F]{3}){1,2}$')
    styleable = ['fore', 'back']
    
    def __init__(self, cfg):
        super(PrintAction, self).__init__(cfg)
        
        for part in self.styleable:
            if part in self.cfg:
                clr = self.non_alnum.sub('', self.cfg[part])
                if self.hex_colour.match(clr) is not None:
                    clr = '#%s' % clr
                self.cfg[part] = clr
                
        style = ''
        if 'fore' in self.cfg:
            style = '%s color: %s;' % (style, self.cfg['fore'])
            
        if 'back' in self.cfg:
            style = '%s background-color: %s;' % (style, self.cfg['back'])
            
        if 'bold' in self.cfg:
            style = '%s font-weight: bold;' % style
        
        if 'italic' in self.cfg:
            style = '%s font-style: italic' % style
        
        self.style = style
        
    def run_on(self, line):
        return '<span style="%s">%s</span><br />' % (
            self.style, cgi.escape(line)
        )
