# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2014 - 2015 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
An output object for handling processed documents
"""

import sys
import os
import io
import contextlib

class Output(object):
    """Object living for a whole file/command operation, handling the output.
    
    When opening a file it has already opened earlier, the file is appended to
    (like awk).
    
    """
    def __init__(self):
        self._seen_filenames = set()
    
    def get_filename(self, opts, filename):
        """Queries the output attribute from the Options and returns it.
        
        If replace_pattern is True (by default) and the attribute contains a 
        '*', it is replaced with the full path of the specified filename, 
        but without extension. It the attribute contains a '?', it is 
        replaced with the filename without path and extension.
        
        If '-' is returned, it denotes standard output.
        
        """
        if not opts.output:
            return '-'
        elif opts.replace_pattern:
            path, ext = os.path.splitext(filename)
            directory, name = os.path.split(path)
            return opts.output.replace('?', name).replace('*', path)
        else:
            return opts.output
    
    @contextlib.contextmanager
    def file(self, opts, filename, encoding):
        """Return a context manager for writing to.
        
        If you set encoding to "binary" or False, the file is opened in binary
        mode and you should encode the data you write yourself.
        
        """
        if not filename or filename == '-':
            filename, mode = sys.stdout.fileno(), 'w'
        #elif filename == '@http':
            
        else:
            if filename not in self._seen_filenames:
                self._seen_filenames.add(filename)
                if opts.backup_suffix and os.path.exists(filename):
                    shutil.copy(filename, filename + opts.backup_suffix)
                mode = 'w'
            else:
                mode = 'a'
        if encoding in (False, "binary"):
            f = io.open(filename, mode + 'b')
        else:
            f = io.open(filename, mode, encoding=encoding)
        try:
            yield f
        finally:
            f.close()
