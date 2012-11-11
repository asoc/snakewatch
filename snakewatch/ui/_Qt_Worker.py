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
from multiprocessing import Process, Pipe

from snakewatch import enum, LOG_FILE, LOG_LEVEL

CoordSig = enum(
    'Kill', 'Start', 'Pause'
)

WorkerSig = enum(
    'Inited', 'Started', 'Output', 'Interrupt', 'Waiting', 'Finished'
)

class ParentDiedError(Exception):
    pass

class KilledError(Exception):
    pass

class Worker(object):
    def __init__(self, event_queue, input_type, cfg, **kwargs):
        recv_pipe, self.send_pipe = Pipe(False)
        self.proc = Process(
            target=_Worker,
            name='Snakewatch [%d] Worker' % os.getpid(),
            args=[
                os.getpid(), recv_pipe, event_queue, 
                input_type, cfg,
            ],
            kwargs=kwargs
        )
        self.proc.start()
        self.pid = self.proc.pid
        self.cfg = cfg
        
class _Worker(object):
    def __init__(self, parent_pid, pipe, event_queue, 
                 input_type, cfg, **kwargs):
        self.logger = logging.getLogger('Worker.%d.%d' % (
            parent_pid, os.getpid()
        ))
        self.logger.debug('Initializing worker')
        
        self.input = input_type(**kwargs)
        self.cfg = cfg
        self.pipe = pipe
        self.event_queue = event_queue
        self.parent_pid = parent_pid
        self.start = False
        
        try:
            self.add_to_queue(WorkerSig.Inited, self.input.name())
            while not self.start:
                self.poll_callback(5)
                
            self.logger.info('Starting watch.')
            
            self.input.watch(
                self.started_callback, 
                self.output_callback, 
                self.int_callback,
                self.poll_callback
            )
        except ParentDiedError:
            self.logger.warn('Parent died.')
        except KilledError:
            self.logger.debug('Received kill signal.')
        except Exception:
            self.logger.exception('Watch interrupted.')
        
        self.input.close()
        self.add_to_queue(WorkerSig.Finished)
        self.logger.info('Worker stopping.')
    
    def add_to_queue(self, action, obj=None):
        self.event_queue.put((os.getpid(), action, obj))
    
    def poll_callback(self, timeout=-1):
        if timeout < 0:
            sig = self.pipe.poll()
        else:
            sig = self.pipe.poll(timeout)
            
        if sig:
            try:
                sig = self.pipe.recv()
            except EOFError:
                raise ParentDiedError()
            
            if sig == CoordSig.Pause:
                self.logger.info('Pausing.')
                self.start = False
                try:
                    self.add_to_queue(WorkerSig.Waiting)
                    while not self.start:
                        sig = self.pipe.recv()
                        self.process_signal(sig)
                    self.started_callback()
                except EOFError:
                    raise ParentDiedError()
            
            self.process_signal(sig)
                
    def process_signal(self, sig):
        if sig == CoordSig.Kill:
            raise KilledError()
        
        if sig == CoordSig.Start:
            self.start = True
        
    def started_callback(self):
        self.add_to_queue(WorkerSig.Started)
        
    def output_callback(self, line):
        line = self.cfg.match(line)
        if line != '':
            self.add_to_queue(WorkerSig.Output, line)
        
    def int_callback(self, error):
        self.add_to_queue(WorkerSig.Interrupt, error)
