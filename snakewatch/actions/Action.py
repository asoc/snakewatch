import re
from abc import ABCMeta, abstractmethod, abstractproperty

class Action(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, cfg):
        self.cfg = cfg
    
    def matches(self, line):
        if re.match(self.cfg['regex'], line):
            return True
        return False
    
    @abstractmethod
    def run_on(self, line):
        print ''