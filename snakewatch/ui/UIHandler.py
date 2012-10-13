from abc import ABCMeta, abstractmethod, abstractproperty

__AF_ERR = 'Abstract UIHandler functions cannot be called directly.'

class UIHandler:
    __metaclass__ = ABCMeta
    
    def __init__(self, *args):
        pass
    
    @abstractmethod
    def run(self, input, config):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def close(self):
        raise RuntimeError(__AF_ERR)