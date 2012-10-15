from abc import ABCMeta, abstractmethod, abstractproperty

from input import File

__AF_ERR = 'Abstract UIHandler functions cannot be called directly.'

class UI(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, *args):
        pass
    
    @abstractmethod
    def run(self, start_input, start_config):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def handle_signal(self, signum, frame):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def started_callback(self):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def output_callback(self, line):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def int_callback(self, error):
        raise RuntimeError(__AF_ERR)
    
    @abstractmethod
    def quit(self):
        for fp in File.FileInput.open_files:
            fp.close()