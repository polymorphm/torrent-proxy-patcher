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
