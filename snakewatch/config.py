import json
import os
import importlib

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
        self.check_actions()
        
    def check_actions(self):
        for entry in self.cfg:
            name = entry['action']
            module = importlib.import_module('action.%s' % name) 
            
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
        user_default = os.path.expanduser(os.path.join(
            '~', '.snakewatch', 'default.json'
        ))
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