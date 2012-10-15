from abc import ABCMeta, abstractmethod, abstractproperty

class Input():
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def name(self):
        return None
    
    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def watch(self, started_callback, output_callback, int_callback):
        pass
    
    @abstractmethod
    def close(self):
        pass