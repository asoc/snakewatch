import sys

from snakewatch.input._Input import Input

class STDInput(Input):
    def __init__(self):
        self.closed = True
    
    def name(self):
        return 'stdin'
    
    def open(self):
        self.closed = False
    
    def watch(self, started_callback, output_callback, int_callback):
        self.open()
        started_callback()
        
        while not self.closed:
            try:
                line = sys.stdin.readline()
                if line != '':
                    output_callback(line)
            except:
                pass
            
    
    def close(self):
        self.closed = True
    
