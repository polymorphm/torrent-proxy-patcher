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

BDECODE_LEVEL_MAX = 100

class BdecodeError(Exception):
    pass

class TooLargeBdecodeError(BdecodeError):
    pass

class InvalidValueBdecodeError(ValueError):
    pass

def bdecode_pos(b_val, curr_pos, _level=None):
    assert isinstance(b_val, bytes)
    
    if _level is None:
        _level = 1
    
    if _level > BDECODE_LEVEL_MAX:
        raise TooLargeBdecodeError('level is too large')
    
    if b_val[curr_pos:curr_pos+1] in (
            b'0', b'1', b'2', b'3', b'4',
            b'5', b'6', b'7', b'8', b'9',
            ):
        val_len = b_val[curr_pos:curr_pos+1]
        curr_pos += 1
        
        while True:
            if b_val[curr_pos:curr_pos+1] == b':':
                curr_pos += 1
                
                break
            
            if b_val[curr_pos:curr_pos+1] not in (
                    b'0', b'1', b'2', b'3', b'4',
                    b'5', b'6', b'7', b'8', b'9',
                    ):
                raise InvalidValueBdecodeError
            
            val_len += b_val[curr_pos:curr_pos+1]
            curr_pos += 1
        
        val_len = int(val_len)
        
        val = b_val[curr_pos:curr_pos+val_len]
        curr_pos += val_len
        
        if len(val) != val_len:
            raise InvalidValueBdecodeError
        
        return val, curr_pos
    
    if b_val[curr_pos:curr_pos+1] == b'i':
        curr_pos += 1
        val = b''
        
        while True:
            if b_val[curr_pos:curr_pos+1] == b'e':
                curr_pos += 1
                
                break
            
            if b_val[curr_pos:curr_pos+1] not in (
                    b'0', b'1', b'2', b'3', b'4',
                    b'5', b'6', b'7', b'8', b'9', b'-',
                    ):
                raise InvalidValueBdecodeError
            
            val += b_val[curr_pos:curr_pos+1]
            curr_pos += 1
        
        try:
            val = int(val)
        except ValueError:
            raise InvalidValueBdecodeError
        
        return val, curr_pos
    
    if b_val[curr_pos:curr_pos+1] == b'l':
        curr_pos += 1
        val = []
        
        while True:
            if b_val[curr_pos:curr_pos+1] == b'e':
                curr_pos += 1
                
                break
            
            if not b_val[curr_pos:curr_pos+1]:
                raise InvalidValueBdecodeError
            
            # recursion
            
            i_val, pos = bdecode_pos(b_val, curr_pos, _level=_level+1)
            curr_pos = pos
            
            val.append(i_val)
        
        val = tuple(val)
        
        return val, curr_pos
    
    if b_val[curr_pos:curr_pos+1] == b'd':
        curr_pos += 1
        val = {}
        
        while True:
            if b_val[curr_pos:curr_pos+1] == b'e':
                curr_pos += 1
                
                break
            
            if not b_val[curr_pos:curr_pos+1]:
                raise InvalidValueBdecodeError
            
            # recursion
            
            k_val, pos = bdecode_pos(b_val, curr_pos, _level=_level+1)
            curr_pos = pos
            
            v_val, pos = bdecode_pos(b_val, curr_pos, _level=_level+1)
            curr_pos = pos
            
            val[k_val] = v_val
        
        return val, curr_pos
    
    raise InvalidValueBdecodeError('unknown type: {!r}'.format(b_val[curr_pos:curr_pos+1]))

def bdecode(b_val):
    val, pos = bdecode_pos(b_val, 0)
    
    return val
