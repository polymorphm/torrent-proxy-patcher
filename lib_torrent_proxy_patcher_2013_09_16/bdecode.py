# -*- mode: python; coding: utf-8 -*-
#
# Copyright (c) 2013 Andrej Antonov <polymorphm@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
