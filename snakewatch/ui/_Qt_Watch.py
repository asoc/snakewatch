import colorama
import logging

from PySide.QtGui import *
from PySide.QtCore import *

from snakewatch.ui._Qt_Queue import add_event

_COLOURS = {
    #            DIM         NORMAL      BRIGHT
    'BLACK':    ['000',     '000',      '666'],
    'RED':      ['600',     'A00',      'F00'],
    'GREEN':    ['060',     '0A0',      '0F0'],
    'YELLOW':   ['660',     'AA0',      'FF0'],
    'BLUE':     ['006',     '00A',      '00F'],
    'MAGENTA':  ['606',     'A0A',      'F0F'],
    'CYAN':     ['066',     '0AA',      '0FF'],
    'WHITE':    ['999',     'CCC',      'FFF'],
}

def convert_to_html(line):
    line = line.replace(colorama.Style.RESET_ALL, '')
    closers = ''
    
    style = 1
    if colorama.Style.DIM in line:
        style = 0
    elif colorama.Style.BRIGHT in line:
        style = 2
    
    for clr in _COLOURS.keys():
        fore = getattr(colorama.Fore, clr)
        if fore in line:
            line = line.replace(
                fore, 
                '<span style="color: #%s;">' % _COLOURS[clr][style]
            )
            closers = '%s</span>' % closers
            
        back = getattr(colorama.Back, clr)
        if back in line:
            line = line.replace(
                back,
                '<span style="background-color: #%s;">' % _COLOURS[clr][style]
            )
            closers = '%s</span>' % closers
    
    line = line.replace('\n', '<br />')
    
    return '%s%s' % (line, closers)

class Coord(object):
    def __init__(self, thread, tab, cfg):
        self.id = str(id(thread))
        self.thread = thread
        self.tab = tab
        self.cfg = cfg
        
    def append_text(self, line):
        self.tab.moveCursor(QTextCursor.End)
        line = convert_to_html(line)
        self.tab.insertHtml(line)

class Thread(QThread):
    #update = Signal(str, str, list)
    closed = Signal(str)
    
    def __init__(self, input_type, callback, **kwargs):
        super(Thread, self).__init__()
        self.input_type = input_type
        self.callback = callback
        self.kwargs = kwargs
        self.input = None
        
    def run(self):
        self.input = self.input_type(**self.kwargs)
        id_info = '%s [%s]' % (
            self.id, self.name()
        )
        logging.debug('Starting watch in ID %s' % id_info)
        try:
            self.input.watch(
                self.started_callback, 
                self.output_callback, 
                self.int_callback
            )
        except Exception as err:
            logging.exception('Cannot start watcher')
        
        self.closed.emit(self.id)
        logging.debug('Watch ended in ID %s' % id_info)
        
    def name(self):
        if self.input is None:
            return 'None'
        return self.input.name()
        
    @Slot(str)
    def stop_watching(self, id):
        if id is not None and id != self.id:
            return
        
        self.input.close()
        
    def started_callback(self):
        add_event(self.callback, self.id, 'started', args=[self.name(),])
        #self.update.emit(self.id, 'started', [self.name(),])
        
    def output_callback(self, line):
        add_event(self.callback, self.id, 'output', args=[line,])
        #self.update.emit(self.id, 'output', [line,])
        
    def int_callback(self, error):
        add_event(self.callback, self.id, 'int', [error,])
        #self.update.emit(self.id, 'int', [error,])

class Tab(QTextBrowser):
    def __init__(self, thread_id):
        super(Tab, self).__init__()
        self.thread_id = thread_id
        self.closed_by_gui = False