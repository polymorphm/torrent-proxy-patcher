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

import unittest
from . import bdecode

def test_single_decode_encode(test_case, b_value):
    from . import bencode
    
    value, pos = bdecode.bdecode_pos(b_value, 0)
    
    test_case.assertIsNotNone(value)
    test_case.assertEqual(len(b_value), pos)
    
    result = bencode.bencode(value)
    
    test_case.assertIsInstance(result, bytes)
    test_case.assertEqual(b_value, result)
    
    b_value_extra = b_value + b'extra'
    value_extra, pos_extra = bdecode.bdecode_pos(b_value_extra, 0)
    
    test_case.assertEqual(value, value_extra)
    test_case.assertEqual(pos, pos_extra)

class TestBdecode(unittest.TestCase):
    def test_decode_encode_str(self):
        test_single_decode_encode(self, b'4:spam')
    
    def test_decode_encode_str_2(self):
        test_single_decode_encode(self, b'0:')
    
    def test_decode_encode_int(self):
        test_single_decode_encode(self, b'i3e')
    
    def test_decode_encode_int_2(self):
        test_single_decode_encode(self,  b'i-3e')
    
    def test_decode_encode_int_3(self):
        test_single_decode_encode(self, b'i0e')
    
    def test_decode_encode_list(self):
        test_single_decode_encode(self, b'l4:spam4:eggse')
    
    def test_decode_encode_list_2(self):
        test_single_decode_encode(self, b'le')
    
    def test_decode_encode_dict(self):
        test_single_decode_encode(self, b'd3:cow3:moo4:spam4:eggse')
    
    def test_decode_encode_dict_2(self):
        test_single_decode_encode(self, b'd4:spaml1:a1:bee')
    
    def test_decode_encode_dict_3(self):
        test_single_decode_encode(self, b'd9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')
    
    def test_decode_encode_dict_4(self):
        test_single_decode_encode(self, b'de')
    
    def test_bdecode_error_type(self):
        self.assertTrue(issubclass(bdecode.TooLargeBdecodeError, bdecode.BdecodeError))
        self.assertTrue(issubclass(bdecode.BdecodeError, Exception))
        self.assertTrue(issubclass(bdecode.InvalidValueBdecodeError, ValueError))
    
    def test_decode_invalid_value(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l4:spamx4:eggse')
    
    def test_decode_invalid_value_2(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l4:spam4:eggs')
    
    def test_decode_invalid_value_3(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l4:spam4:eggs4')
    
    def test_decode_invalid_value_4(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l4:spam4:eggs4:')
    
    def test_decode_invalid_value_5(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l4:spam4:eggs4:x')
    
    def test_decode_invalid_value_6(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'i')
    
    def test_decode_invalid_value_7(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'l')
    
    def test_decode_invalid_value_8(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'd')
    
    def test_decode_invalid_value_9(self):
        with self.assertRaises(bdecode.InvalidValueBdecodeError):
            result = bdecode.bdecode(b'd4:spam')
    
    def test_decode_too_large(self):
        b_value = \
                b'llllllllllllllllllllllllllllllllllllllllllllllllllllllllllll' \
                b'llllllllllllllllllllllllllllllllllllllllllllllllllllllllllll'
        
        with self.assertRaises(bdecode.TooLargeBdecodeError):
            result = bdecode.bdecode(b_value)
    
    def test_decode_too_large_2(self):
        b_value = \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:' \
                b'd0:d0:d0:d0:d0:d0:d0:d0:d0:d0:'
        
        with self.assertRaises(bdecode.TooLargeBdecodeError):
            result = bdecode.bdecode(b_value)
