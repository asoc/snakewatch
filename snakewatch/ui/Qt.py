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
import pkgutil
import importlib

from PySide.QtGui import *
from PySide.QtCore import *

from snakewatch import NAME, VERSION, LOG_FILE, SysToLogging
from snakewatch import config
from snakewatch import action as action_module
from snakewatch.input import File
from snakewatch.ui._Qt_WorkerCoord import WorkerCoord, WorkerEvent
from snakewatch.ui._Qt_Worker import WorkerSig

class QtUI(QMainWindow):
    def __init__(self, *args):
        self.app = QApplication([])
        self.app.setOrganizationName('Illogi.ca/l Development')
        self.app.setOrganizationDomain('illogi.ca')
        self.app.setApplicationName(NAME.title())
        self.app.setApplicationVersion(VERSION)
        self.app.aboutToQuit.connect(self.before_quit)
        
        self.logger = logging.getLogger('UI')
        sys.stderr = SysToLogging(logging.ERROR)
        sys.stdout = SysToLogging(logging.INFO)
        
        self.watchers = {}
        
        self.logger.debug('Application Initialized')
        
        self.load_settings()
        self.initMainWindow()
        self.initMenuBar()
        self.logger.debug('UI Init Finished')
        
        self.coord = WorkerCoord(self)
        
        self.action_overrides = {}
        for imp, name, ispkg in pkgutil.iter_modules(action_module.__path__):
            if ispkg or not name.startswith('_Qt_'):
                continue
            action = name.split('_Qt_')[1]
            module = importlib.import_module('snakewatch.action.%s' % name)
            action_callable = '%sAction' % action
            self.action_overrides[action] = getattr(module, action_callable)
    
    def load_settings(self):
        self.settings = QSettings()
        
    
    def initMainWindow(self):
        super(QtUI, self).__init__()
        self.setMinimumSize(600, 400)
        self.resize(
            self.settings.value('mainWindow/width', self.minimumWidth()),
            self.settings.value('mainWindow/height', self.minimumHeight())
        )
        
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
    
    def warn(self, message, exception=None):
        if exception is not None:
            message = '%s\n\n%s' % (message, exception)
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Warning')
        dialog.setText(message)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.show()
        dialog.exec_()
    
    def customEvent(self, event):
        if isinstance(event, WorkerEvent):
            self.watcher_update(event.data)
    
    def new_watch_tab(self, pid, title):
        tab = QTextBrowser()
        tab.pid = pid
        tab.closed_by_gui = False
        self.tabs.addTab(tab, title)
        self.watchers[pid] = tab
        return tab
    
    def watcher_update(self, queue_data):
        pid, action, obj = queue_data
        
        
        if action == WorkerSig.Inited:
            watch_tab = self.new_watch_tab(pid, obj)
            self.coord.start_worker(pid)
            return
            
        try:
            watch_tab = self.watchers[pid]
        except KeyError:
            self.coord.stop(pid)
            return
        finally:
            if action == WorkerSig.Finished:
                self.coord.close_worker(pid)
                try:
                    watch_tab = self.watchers.pop(pid)
                    self.tabs.removeTab(self.tabs.indexOf(watch_tab))
                except Exception:
                    pass
                return
        
        if action == WorkerSig.Started:
            pass
        if action == WorkerSig.Output:
            watch_tab.moveCursor(QTextCursor.End)
            watch_tab.insertHtml(obj)
        elif action == WorkerSig.Interrupt:
            logging.error(obj)
    
    @Slot(int)
    def closing_tab(self, index):
        tab = self.tabs.widget(index)
        tab.closed_by_gui = True
        self.coord.stop_worker(tab.pid)
        self.tabs.removeTab(index)
    
    def action_stop_watcher(self):
        watcher = self.tabs.currentWidget()
        self.coord.stop(watcher.pid)
    
    def action_file_open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')[0]
        if filename == '':
            return
        
        input_type = File.FileInput
        kwargs = {
            'filename': filename,
            'readback': -1,
        }
        
        self.coord.spawn_worker(input_type, **kwargs)
        
    def run(self, start_input, start_config):
        self.coord.start()
        self.show()
        
        self.logger.debug("Starting main event loop")
        self.app.exec_()
    
    def handle_signal(self, signum, frame):
        pass
    
    def before_quit(self):
        self.coord.stop_workers()
        self.coord.wait()
        self.settings.setValue('mainWindow/width', self.width())
        self.settings.setValue('mainWindow/height', self.height())
            
    def action_file_quit(self):
        self.app.quit()
        
class ChooseInputDialog(QDialog):
    def __init__(self, *args):
        super(ChooseInputDialog, self).__init__(args)
