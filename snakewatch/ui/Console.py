from UIHandler import UIHandler

class ConsoleHandler(UIHandler):
    def __init__(self, *args):
        super(ConsoleHandler, self).__init__(args)
        
    def run(self, input, config):
        pass
    
    def close(self):
        pass