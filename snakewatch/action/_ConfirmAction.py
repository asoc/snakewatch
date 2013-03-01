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

from abc import ABCMeta, abstractmethod

from snakewatch.util import NotConfirmedError
from snakewatch.action._Action import Action


class ConfirmAction(Action):
    '''An abstract Action that requests user confirmation

    If any confirm_config request fails, snakewatch will not run.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, cfg, ui_confirm, required_attributes=list()):
        super(ConfirmAction, self).__init__(cfg, required_attributes)

        if not ui_confirm(self.confirm_message()):
            raise NotConfirmedError()

    @abstractmethod
    def confirm_message(self):
        pass
