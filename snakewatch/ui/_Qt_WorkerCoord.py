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
import logging
from multiprocessing import Queue

from PySide.QtCore import QCoreApplication, QEvent, QThread

from snakewatch import enum
from snakewatch import config
from snakewatch.ui._Qt_Worker import Worker, CoordSig

class WorkerEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, data):
        super(WorkerEvent, self).__init__(WorkerEvent.EVENT_TYPE)
        self.data = data

class WorkerCoord(QThread):
    workers = {}
    finished_worker_pipes = {}
    
    def __init__(self, parent):
        super(WorkerCoord, self).__init__()
        self.parent = parent
        self.event_queue = Queue()
        self.logger = logging.getLogger('WorkerCoord')
    
    def run(self):
        self.logger.info('Starting queue poll loop')
        while True:
            queue_data = self.event_queue.get()
            if queue_data is None:
                break
            QCoreApplication.postEvent(self.parent, WorkerEvent(queue_data))
        self.logger.info('Exiting queue poll loop')
    
    def stop_workers(self):
        self.event_queue.put(None)
        self.logger.info('Sending kill signal to all workers')
        
        for p_id in WorkerCoord.workers.keys():
            self.stop_worker(p_id)
        
        self.logger.info('Done')
            
    def start_worker(self, pid):
        try:
            worker = WorkerCoord.workers[pid]
        except KeyError:
            return
        
        worker.send_pipe.send(CoordSig.Start)
        
    def stop_worker(self, pid=None):
        if pid is not None:
            try:
                worker = WorkerCoord.workers.pop(pid)
            except KeyError:
                return
            
            self.logger.info('Sending kill signal to worker PID %d' % pid)
            worker.send_pipe.send(CoordSig.Kill)
            WorkerCoord.finished_worker_pipes[pid] = worker.send_pipe
            
    def close_worker(self, pid):
        try:
            pipe = WorkerCoord.finished_worker_pipes.pop(pid)
        except KeyError:
            pass
        else:
            pipe.close()
            
    def spawn_worker(self, input_type, cfg=None, **kwargs):
        if cfg is None:
            cfg = config.DefaultConfig()
            
        for override in self.parent.action_overrides:
            for i in range(0, len(cfg.actions)):
                if cfg.actions[i].name != override.title():
                    continue
                override_action = self.parent.action_overrides[override]
                cfg.actions[i] = override_action(cfg.actions[i].raw_cfg)
                
        worker = Worker(self.event_queue, input_type, cfg, **kwargs)
        WorkerCoord.workers[worker.pid] = worker
        return worker
    