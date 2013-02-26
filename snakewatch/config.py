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
import json
import os
import importlib

from snakewatch import USER_PATH


def lower_keys(x):
    '''Recursively make all keys lower-case'''
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    if isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.items())
    return x


class Config(object):
    '''An in-memory instance of a user .cfg file'''

    available_actions = {}
    
    def __init__(self, cfg_file):
        if isinstance(cfg_file, str):
            fp = open(cfg_file, 'r')
            self.cfg = json.load(fp)
            fp.close()
            self.source = cfg_file
        elif isinstance(cfg_file, file):
            self.cfg = json.load(cfg_file)
            self.source = cfg_file.name
        elif isinstance(cfg_file, list):
            self.cfg = cfg_file
            self.source = 'default'
        self.actions = []
        self.cfg = lower_keys(self.cfg)
        self.check_actions()
        
    def check_actions(self):
        '''Create an action instance for each entry in the config'''
        ptrn = re.compile('[\W]+')

        for entry in self.cfg:
            name = ptrn.sub('', entry['action']).title()
            entry['action'] = name
            try:
                action = Config.available_actions[name]
            except KeyError:
                action_module = importlib.import_module('snakewatch.action.%s' % name)

                action_object_name = '%sAction' % name
                Config.available_actions[name] = action = getattr(action_module, action_object_name)

            self.actions.append(action(entry))
        
    def match(self, line):
        '''Perform the first action where action.matches(line) is True

        If a match is found, return the result of action.run_on(line)
          or '' if the result is None

        If no match is found, return the
        '''
        for action in self.actions:
            if action.matches(line):
                result = action.run_on(line)
                if result is None:
                    return ''
                return result
        return line


class DefaultConfig(Config):
    '''A default default config.

    This config is only used when <USER_PATH>/default.json does not exist,
    and uses Print for all inputs.
    '''

    def __init__(self, ui, use_file=True):
        user_default = DefaultConfig.file_for(ui)
        use_builtin = False
        if use_file and os.path.exists(user_default):
            try:
                with open(user_default) as fp:
                    super(DefaultConfig, self).__init__(fp)
            except Exception as err:
                use_builtin = True

        if use_builtin:
            cfg = [
                {
                    'regex': '.*',
                    'action': 'Print',
                },
            ]
            super(DefaultConfig, self).__init__(cfg)

    @classmethod
    def file_for(cls, ui):
        return os.path.join(USER_PATH, 'default-%s.json' % ui.__class__.__name__)
