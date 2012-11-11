import Queue
from PySide.QtCore import QEvent

event_queue = Queue.Queue()

class Event(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, callback):
        super(Event, self).__init__(Event.EVENT_TYPE)
        self.callback = callback

def add_event(func, *args, **kwargs):
    def ev():
        return func(*args, **kwargs)
    event_queue.put(ev)