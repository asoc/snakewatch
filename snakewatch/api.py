"""
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
"""
from __future__ import (
    print_function, unicode_literals, absolute_import, division
)

from .action._Action import Action
from .action._CallbackAction import CallbackAction
from .mode.Console import ConsoleMode
from .util import get_read_object


class SnakewatchAPI(object):
    class StopWatching(Exception):
        pass

    def __init__(self, watch=None, config=None, start_at=-1, start_at_byte=-1,
                 remove_default_actions=True):
        self.watch = get_read_object(
            watch is None, watch, start_at, start_at_byte
        )
        self.handler = ConsoleMode()
        self.handler.quiet = True
        self.handler.pre_run(self.watch, config)

        if remove_default_actions:
            self.actions = self.handler.cfg.actions = []
        else:
            self.actions = self.handler.cfg.actions

        self.start_at = start_at

    def set_callback(self, pattern, callback, index=-1, replace=False,
                     **config):
        if not callable(callback):
            raise TypeError('callback must be callable')

        config['regex'] = pattern

        ca = CallbackAction(self, config, callback)

        if index is None:
            index = -1

        if isinstance(index, Action):
            index = self.actions.index(index)

        if index < 0:
            self.actions.append(ca)
        elif replace:
            self.actions[index] = ca
        else:
            self.actions.insert(index, ca)

        return ca

    def remove_callback(self, action):
        self.actions.remove(action)

    def run(self):
        try:
            self.handler.run(True)
        except SnakewatchAPI.StopWatching:
            pass

    def stop(self):
        self.watch.close()
