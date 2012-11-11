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
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    if isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.items())
    return x

class Config(object):
    available_actions = {}
    
    def __init__(self, cfg, *args):
        if isinstance(cfg, str):
            fp = open(cfg, 'r')
            self.cfg = json.load(fp)
            fp.close()
        elif isinstance(cfg, list):
            self.cfg = cfg
        self.actions = []
        self.cfg = lower_keys(self.cfg)
        self.check_actions()
        
    def check_actions(self):
        ptrn = re.compile('[\W]+')
        for entry in self.cfg:
            name = ptrn.sub('', entry['action']).title()
            entry['action'] = name
            module = importlib.import_module('snakewatch.action.%s' % name) 
            
            if name not in Config.available_actions:
                action = '%sAction' % name
                Config.available_actions[name] = getattr(module, action)
                
            self.actions.append(Config.available_actions[name](entry))
        
    def match(self, line):
        for action in self.actions:
            if action.matches(line):
                result = action.run_on(line)
                if result is None:
                    return ''
                return result
        return line

class DefaultConfig(Config):
    def __init__(self):
        user_default = os.path.join(USER_PATH, 'default.json')
        if os.path.exists(user_default):
            cfg = user_default
        else:
            cfg = [
                {
                    'regex': '.*',
                    'action': 'Print',
                },
            ]
        
        super(DefaultConfig, self).__init__(cfg)
