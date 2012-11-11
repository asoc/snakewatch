'''
This file is part of snakewatch.

snakewatch is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

snakewatch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with snakewatch.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
import time
import logging
import Queue

from PySide.QtGui import *
from PySide.QtCore import *

from snakewatch import NAME, VERSION, LOG_FILE, SysToLogging
from snakewatch import config
from snakewatch.input import File
from snakewatch.ui import _Qt_Watch as Watch
from snakewatch.ui._Qt_Queue import *

class ThreadCoord(QThread):
    threads = {}
    stop_thread = Signal(str)
    destroy_watcher = Signal(str)
    
    def __init__(self, parent):
        super(ThreadCoord, self).__init__()
        self.parent = parent
        self.destroy_watcher.connect(self.parent.destroy_watcher)
    
    def register(self, thread):
        ThreadCoord.threads[thread.id] = thread
        self.stop_thread.connect(thread.stop_watching)
        thread.closed.connect(self.thread_finished)
    
    @Slot(str)
    def thread_finished(self, id):
        thread = self.threads[id]
        thread.wait()
        self.threads.pop(id)
        self.destroy_watcher.emit(id)
    
    def run(self):
        while True:
            callback = event_queue.get()
            if callback is None:
                break
            QCoreApplication.postEvent(self.parent, Event(callback))
    
    def stop(self, id=None):
        if id is None:
            event_queue.put(None)
        self.stop_thread.emit(id)
        if id is None:
            self.wait()
    
class QtUI(QMainWindow):
    def __init__(self, *args):
        self.app = QApplication([])
        self.app.aboutToQuit.connect(self.before_quit)
        
        sys.stderr = SysToLogging(logging.ERROR)
        sys.stdout = SysToLogging(logging.INFO)
        
        self.watchers = {}
        
        logging.debug('Application Initialized')
        
        self.initMainWindow()
        self.initMenuBar()
        logging.debug('UI Init Finished')
        
        self.dispatch = ThreadCoord(self)
    
    def initMainWindow(self):
        super(QtUI, self).__init__()
        self.setMinimumSize(600, 400)
        
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(sp)
        self.tabs.setParent(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closing_tab)
        
        self.setCentralWidget(self.tabs)
        
    def initMenuBar(self):
        self.app.setApplicationName(NAME)
        self.app.setApplicationVersion(VERSION)
        
        mb = QMenuBar()
        self.setMenuBar(mb)
        
        file_menu = QMenu('File')
        
        action_open = QAction('Open', file_menu)
        action_open.setShortcut(QKeySequence.Open)
        action_open.triggered.connect(self.action_file_open)
        
        file_menu.addAction(action_open)
        file_menu.addSeparator()
        
        if not sys.platform.startswith('darwin'):
            action_quit = QAction('Quit', file_menu)
            action_quit.setShortcut(QKeySequence.Quit)
            action_quit.triggered.connect(self.action_file_quit)
            file_menu.addAction(action_quit)
        
        mb.addMenu(file_menu)
        
        watch_menu = QMenu('Watcher')
        
        action_stop = QAction('Stop', watch_menu)
        action_stop.triggered.connect(self.action_stop_watcher)
        
        watch_menu.addAction(action_stop)
        
        mb.addMenu(watch_menu)
    
    def customEvent(self, event):
        event.callback()
    
    #@Slot(str, str, list)
    def update_watcher(self, id, callback, args):
        if id not in self.watchers:
            return False
        
        watcher = self.watchers[id]
        
        if callback == 'output':
            line = watcher.cfg.match(args[0])
            if line != '':
                watcher.append_text(line)
        elif callback == 'int':
            logging.error(args[0])
        elif callback == 'started':
            self.tabs.setTabText(self.tabs.indexOf(watcher.tab), args[0])
    
    @Slot(int)
    def closing_tab(self, index):
        tab = self.tabs.widget(index)
        tab.closed_by_gui = True
        id = tab.thread_id
        if id in self.watchers:
            watcher = self.watchers[id]
            self.dispatch.stop(id)
        self.tabs.removeTab(index)
        
    @Slot(str)
    def destroy_watcher(self, id):
        if id not in self.watchers:
            return
        
        watcher = self.watchers.pop(id)
        if not watcher.tab.closed_by_gui:
            self.tabs.removeTab(self.tabs.indexOf(watcher.tab))
    
    def action_stop_watcher(self):
        watcher = self.watchers.values()[0]
        watcher.thread.stop.emit(watcher.id)
    
    def action_file_open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')[0]
        if filename == '':
            return
        
        input_type = File.FileInput
        kwargs = {
            'filename': filename,
            'readback': -1,
        }
        
        try:
            thread = Watch.Thread(input_type, self.update_watcher, **kwargs)
            t_id = str(id(thread))
            thread.id = t_id
            
            self.dispatch.register(thread)
            
            tab = Watch.Tab(t_id)
            coord = Watch.Coord(thread, tab, config.DefaultConfig())
            self.watchers[t_id] = coord
            
            self.tabs.addTab(tab, thread.name())
            
            thread.start()
        except Exception as err:
            logging.exception('Cannot start watcher')
        
    def run(self, start_input, start_config):
        logging.debug('Starting Thread Coordinator')
        self.dispatch.start()
        
        self.show()
        
        logging.debug("Starting Main Event Loop")
        self.app.exec_()
    
    def handle_signal(self, signum, frame):
        pass
    
    def before_quit(self):
        logging.debug('Stopping Thread Coordinator')
        self.dispatch.stop()
        self.dispatch.wait()
            
    def action_file_quit(self):
        self.app.quit()
        
class ChooseInputDialog(QDialog):
    def __init__(self, *args):
        super(ChooseInputDialog, self).__init__(args)
