from UIHandler import UIHandler

class QtHandler(UIHandler):
    def __init__(self, *args):
        super(QtHandler, self).__init__(args)
        
    def run(self, start_input, start_config):
        pass

    def handle_signal(self, signum, frame):
        pass
    
    def started_callback(self):
        pass
    
    def output_callback(self, line):
        pass
    
    def int_callback(self, error):
        pass
    
    def quit(self):
        super(QtHandler, self).quit()