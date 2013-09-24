# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2013 Andrej Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import contextlib

try:
    import fcntl
except ImportError:
    # on Microsoft Windows
    
    fcntl = None

def flock(fd):
    if fcntl is None:
        # XXX on Microsoft Windows case -- we ignore lock.
        #       this ignore -- may be lead to error,
        #       and we need alternative implementation
        
        return
    
    fcntl.flock(fd, fcntl.LOCK_EX)

def unflock(fd):
    if fcntl is None:
        # XXX on Microsoft Windows case -- we ignore lock.
        #       this ignore -- may be lead to error,
        #       and we need alternative implementation
        
        return
    
    fcntl.flock(fd, fcntl.LOCK_UN)

@contextlib.contextmanager
def flock_context(path):
    with open(path, 'rb') as lock_fd:
        flock(lock_fd)
        try:
            yield
        finally:
            unflock(lock_fd)
