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
from . import bencode

class TestBencode(unittest.TestCase):
    def test_encode_str(self):
        result = bencode.bencode(b'spam')
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'4:spam',
                result,
                )
    
    def test_encode_str_2(self):
        result = bencode.bencode('spam')
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'4:spam',
                result,
                )
    
    def test_encode_str_3(self):
        result = bencode.bencode(b'')
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'0:',
                result,
                )
    
    def test_encode_int(self):
        result = bencode.bencode(3)
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'i3e',
                result,
                )
    
    def test_encode_int_2(self):
        result = bencode.bencode(-3)
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'i-3e',
                result,
                )
    
    def test_encode_int_3(self):
        result = bencode.bencode(0)
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'i0e',
                result,
                )
    
    def test_encode_list(self):
        result = bencode.bencode(
                ('spam', 'eggs'),
                )
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'l4:spam4:eggse',
                result,
                )
    
    def test_encode_list_2(self):
        result = bencode.bencode(
                ['spam', 'eggs'],
                )
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'l4:spam4:eggse',
                result,
                )
    
    def test_encode_list_3(self):
        result = bencode.bencode(())
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'le',
                result,
                )
    
    def test_encode_dict(self):
        result = bencode.bencode(
                {'cow': 'moo', 'spam': 'eggs'},
                )
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'd3:cow3:moo4:spam4:eggse',
                result,
                )
    
    def test_encode_dict_2(self):
        result = bencode.bencode(
                {'spam': ('a', 'b')},
                )
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'd4:spaml1:a1:bee',
                result,
                )
    
    def test_encode_dict_3(self):
        result = bencode.bencode(
                {'publisher': 'bob', 'publisher-webpage': 'www.example.com', 'publisher.location': 'home'},
                )
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'd9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee',
                result,
                )
    
    def test_encode_dict_4(self):
        result = bencode.bencode({})
        
        self.assertIsInstance(result, bytes)
        self.assertEqual(
                b'de',
                result,
                )
    
    def test_bencode_error_type(self):
        self.assertTrue(issubclass(bencode.TooLargeBencodeError, bencode.BencodeError))
        self.assertTrue(issubclass(bencode.BencodeError, Exception))
    
    def test_encode_invalid_type(self):
        with self.assertRaises(TypeError):
            result = bencode.bencode(123.456)
    
    def test_encode_invalid_type_2(self):
        with self.assertRaises(TypeError):
            result = bencode.bencode(None)
    
    def test_encode_too_large(self):
        value = {'cow': 'moo'}
        value['spam'] = value
        
        with self.assertRaises(bencode.TooLargeBencodeError):
            result = bencode.bencode(value)
    
    def test_encode_too_large_2(self):
        def create_value(level):
            value = {'cow': 'moo'}
            top_value = value
            
            for level_i in range(level):
                top_value['spam'] = {}
                top_value = top_value['spam']
                top_value['yet_cow'] = 'moo'
            
            return value
        
        value_A = create_value(90)
        result_A = bencode.bencode(value_A)
        
        self.assertIsInstance(result_A, bytes)
        
        value_B = create_value(110)
        with self.assertRaises(bencode.TooLargeBencodeError):
            result_B = bencode.bencode(value_B)
    
    def test_encode_too_large_3(self):
        def create_value(level):
            value = ['spam']
            top_value = value
            
            for level_i in range(level):
                top_value.append([])
                top_value = top_value[len(top_value) - 1]
                top_value.append('yet_spam')
            
            return tuple(value)
        
        value_A = create_value(90)
        result_A = bencode.bencode(value_A)
        
        self.assertIsInstance(result_A, bytes)
        
        value_B = create_value(110)
        with self.assertRaises(bencode.TooLargeBencodeError):
            result_B = bencode.bencode(value_B)
