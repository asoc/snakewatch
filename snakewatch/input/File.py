"""
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
"""

from __future__ import print_function, absolute_import, unicode_literals, division

import six
import os
import time

try:
    from pathlib import Path
except ImportError:
    Path = None

from ._Input import Input


class FileInput(Input):
    """An Input that reads from a system file"""

    def __init__(self, filename, readback=-1, readbytes=-1):
        self.filename = filename
        self.readback = readback
        self.readbytes = readbytes
        self.reopen = True
        self.has_opened = False
        self.fp = None
        self.where = 0

    def name(self):
        if isinstance(self.filename, Path):
            return self.filename.name
        return os.path.basename(self.filename)

    def open(self):
        if isinstance(self.filename, Path):
            self.fp = self.filename.open('rb' if six.PY3 else 'r')
        else:
            self.fp = open(self.filename, 'rb' if six.PY3 else 'r')

        if not self.has_opened:
            self.has_opened = True
            if self.readbytes >= 0:
                self.fp.seek(self.readbytes)
            if self.readback > -1:
                self.fp.seek(0, os.SEEK_END)
                if self.readback > 0:
                    hit_start = False
                    while self.readback > 0:
                        if self.fp.read(1) == '\n':
                            self.readback -= 1
                        try:
                            self.fp.seek(-2, os.SEEK_CUR)
                        except IOError:
                            hit_start = True
                            break

                    if hit_start:
                        self.fp.seek(0)
                    else:
                        self.fp.seek(2, os.SEEK_CUR)

    def watch(self, started_callback, output_callback, int_callback, poll_callback=None):
        while self.reopen:
            try:
                if poll_callback:
                    poll_callback()
                self.open()
            except Exception as err:
                int_callback('{}\n{!s}'.format(self.filename, err))
                time.sleep(1)
                self.fp = None
            else:
                started_callback()

            while self.fp and not getattr(self.fp, 'closed', True):
                if poll_callback:
                    poll_callback()

                line = self.readline(int_callback)

                if line:
                    output_callback(line)
                else:
                    time.sleep(0.1)

    def readline(self, int_callback):
        """Read a line from the file.

        If the file has been truncated, or cannot be read from, close the file handle,
        set the readback to start at the beginning, and let the watcher re-open the file.
        """
        try:
            if isinstance(self.filename, Path):
                fs = self.filename.stat()
            else:
                fs = os.stat(self.filename)

            self.where = self.fp.tell()
            if fs.st_size < self.where:
                # File contents has been truncated, so close and reopen the file
                self.re_open()
                return ''
            line = self.fp.readline()

            if six.PY3:
                line = line.decode('UTF-8')
        except Exception as err:
            int_callback('\n'.join([str(self.filename), str(err)]))
            self.re_open()
            return ''
        else:
            return line

    def re_open(self):
        self.close()
        self.readback = -1
        self.has_opened = False
        self.reopen = True

    def close(self):
        self.reopen = False
        if not self.fp:
            return
        if six.callable(getattr(self.fp, 'close', None)):
            self.fp.close()
        self.fp = None
