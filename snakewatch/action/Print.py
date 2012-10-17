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

from colorama import Fore, Back, Style

from snakewatch.action._Action import Action

class PrintAction(Action):
    def run_on(self, line):
        style = Style.RESET_ALL
        if 'fore' in self.cfg and hasattr(Fore, self.cfg['fore']):
            style = '%s%s' % (style, getattr(Fore, self.cfg['fore']))
        if 'back' in self.cfg and hasattr(Back, self.cfg['back']):
            style = '%s%s' % (style, getattr(Back, self.cfg['back']))
        if 'style' in self.cfg and hasattr(Style, self.cfg['style']):
            style = '%s%s' % (style, getattr(Style, self.cfg['style']))
        return '%s%s' % (style, line)
