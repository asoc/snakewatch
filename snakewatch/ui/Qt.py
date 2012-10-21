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
from multiprocessing import Process, Pipe
from PySide.QtGui import *
from PySide.QtCore import *

from snakewatch import NAME, VERSION
from snakewatch.input import File

class QtUI(QMainWindow):
    def __init__(self, *args):
        self.app = QApplication([])
        self.app.aboutToQuit.connect(self.before_quit)
        
        self.initMainWindow()
        self.initMenuBar()
        self.watch_processes = []
    
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
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
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
        
    def action_file_open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')[0]
        if filename == '':
            return
        
        p_conn, c_conn = Pipe()
        finput = File.FileInput(filename, pipe=c_conn)
        wt = WatchTab(finput, self, p_conn)
        self.add_tab(wt)
        
    def run(self, start_input, start_config):
        self.show()
        self.app.exec_()
    
    def handle_signal(self, signum, frame):
        pass
    
    def add_tab(self, tab):
        self.tabs.addTab(tab, tab.label())
        
    def close_tab(self, index):
        tab = self.tabs.widget(index)
        tab.close()
        self.tabs.removeTab(index)
    
    def before_quit(self):
        for index in range(0, self.tabs.count()):
            self.close_tab(index)
            
    def action_file_quit(self):
        self.app.quit()
        
class ChooseInputDialog(QDialog):
    def __init__(self, *args):
        super(ChooseInputDialog, self).__init__(args)
    
class WatchTab(QTextBrowser):
    def __init__(self, source, window, p_conn):
        super(WatchTab, self).__init__()
        self.source = source
        self.window = window
        self.pipe = p_conn
        self.process = Process(
            target=source.watch,
            args=(
                self.started_callback, 
                self.output_callback, 
                self.int_callback,
            )
        )
        self.process.start()
        self.window.watch_processes.append(self.process)
        print 'spawned process %d' % self.process.pid
    
    def close(self):
        pid = self.process.pid
        try:
            self.pipe.send('close')
        except Exception:
            print 'terminated %d' % pid
            self.process.terminate()
        else:
            print 'closed %d' % pid
            self.process.join()
        finally:
            self.pipe.close()
            if self.process in self.window.watch_processes:
                self.window.watch_processes.remove(self.process)
    
    def label(self):
        return os.path.basename(self.source.name())
    
    def started_callback(self):
        pass
    
    def output_callback(self, line):
        self.append(line)
    
    def int_callback(self, error):
        pass
