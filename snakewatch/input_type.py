from abc import ABCMeta, abstractmethod, abstractproperty
import os
import time

class _Input():
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

class FileInput(_Input):
    open_files = []
    
    def __init__(self, filename, readback=0):
        self.filename = filename
        self.readback = readback
        self.reopen = True
        self.fp = None
    
    def name(self):
        return self.filename
    
    def open(self):
        self.fp = open(self.filename, 'r')
        self.fp.seek(os.SEEK_END)
        if self.fp not in FileInput.open_files:
            FileInput.open_files.append(self.fp)
    
    def watch(self, started_callback, output_callback, int_callback):
        while self.reopen:
            try:
                self.open()
            except Exception as err:
                int_callback('%s\n%s' % (self.filename, err))
                time.sleep(1)
            else:
                started_callback()
            
            while self.fp is not None and isinstance(self.fp, file) and \
                    not self.fp.closed:
                try:
                    os.stat(self.filename)
                    where = self.fp.tell()
                    line = self.fp.readline()
                except Exception as err:
                    int_callback(err)
                else:
                    if line != '':
                        output_callback(line)
                    else:
                        time.sleep(1)
                        self.fp.seek(where)
        
    def close(self):
        if self.fp is None:
            return
        if isinstance(self.fp, file):
            self.reopen = False
            self.fp.close()
            if self.fp in FileInput.open_files:
                FileInput.open_files.remove(self.fp)
        
class STDInput(_Input):
    def __init__(self):
        pass
    
    def name(self):
        return 'stdin'
    
    def open(self):
        pass
    
    def watch(self, started_callback, output_callback, int_callback):
        pass
    
    def close(self):
        pass
    