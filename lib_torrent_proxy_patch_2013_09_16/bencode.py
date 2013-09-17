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

BENCODE_LEVEL_MAX = 100

class BencodeError(Exception):
    pass

class TooLargeBencodeError(BencodeError):
    pass

def bencode(val, _level=None):
    if _level is None:
        _level = 1
    
    if _level > BENCODE_LEVEL_MAX:
        raise TooLargeBencodeError('level is too large')
    
    if isinstance(val, str):
        val = val.encode()
    
    if isinstance(val, bytes):
        return str(len(val)).encode() + b':' + val
    
    if isinstance(val, int):
        return b'i' + str(val).encode() + b'e'
    
    if isinstance(val, (tuple, list)):
        # recursion
        
        return b'l' + b''.join(bencode(i_val, _level=_level+1) for i_val in val) + b'e'
    
    if isinstance(val, dict):
        # recursion
        
        return b'd' + b''.join(
                bencode(k_val, _level=_level+1) + bencode(val[k_val], _level=_level+1)
                for k_val in sorted(val.keys())
                ) + b'e'
    
    raise TypeError('invalid value type')
