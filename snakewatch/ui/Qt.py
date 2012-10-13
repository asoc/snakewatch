from UIHandler import UIHandler

class QtHandler(UIHandler):
    def __init__(self, *args):
        super(QtHandler, self).__init__(args)
        
    def run(self, start_input, start_config):
        pass

    def close(self):
        pass
    
    def handle_signal(self, signum, frame):
        pass