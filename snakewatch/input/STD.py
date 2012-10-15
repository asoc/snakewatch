from _Input import Input

class STDInput(Input):
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
    