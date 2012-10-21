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

import os
import time

from snakewatch.input._Input import Input

class FileInput(Input):
    open_files = []
    
    def __init__(self, filename, readback=0, pipe=None):
        self.filename = filename
        self.readback = readback
        self.reopen = True
        self.has_opened = False
        self.pipe = pipe
        self.fp = None
        self.where = 0
    
    def name(self):
        return self.filename
    
    def open(self, output_callback, int_callback):
        self.fp = open(self.filename, 'r')
        if not self.has_opened:
            self.has_opened = True
            if self.readback > -1:
                self.fp.seek(0, os.SEEK_END)
                if self.readback > 0:
                    while self.readback > 0:
                        if self.fp.read(1) == '\n':
                            self.readback -= 1
                        self.fp.seek(-2, os.SEEK_CUR)
                    self.fp.seek(2, os.SEEK_CUR)
        if self.fp not in FileInput.open_files:
            FileInput.open_files.append(self.fp)
                
    def watch(self, started_callback, output_callback, int_callback):
        while self.reopen:
            try:
                self.open(output_callback, int_callback)
            except Exception as err:
                int_callback('%s\n%s' % (self.filename, err))
                time.sleep(1)
            else:
                started_callback()
            
            while self.fp is not None and isinstance(self.fp, file) and \
                    not self.fp.closed:
                
                line = self.readline(int_callback)
                if line != '':
                    output_callback(line)
                else:
                    time.sleep(0.1)
                    
                self.process_pipe()
    
    def readline(self, int_callback):
        try:
            fs = os.stat(self.filename)
            self.where = self.fp.tell()
            if fs.st_size < self.where:
                self.fp.seek(0)
            line = self.fp.readline()
        except Exception as err:
            int_callback(err)
            return ''
        else:
            return line
    
    def close(self):
        if self.fp is None:
            return
        if isinstance(self.fp, file):
            self.reopen = False
            self.fp.close()
            if self.fp in FileInput.open_files:
                FileInput.open_files.remove(self.fp)
    
    @classmethod
    def close_all(cls):
        for fi in FileInput.open_files:
            fi.close()
