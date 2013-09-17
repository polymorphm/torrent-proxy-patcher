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

import unittest
from . import torrent_proxy_patcher

class TestUrlPatcher(unittest.TestCase):
    def test_url_patcher(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_url_patcher_2(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com/',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_url_patcher_3(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com/proxy',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/proxy/bt3.rutracker.org/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_url_patcher_4(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com/proxy/',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/proxy/bt3.rutracker.org/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_url_patcher_5(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX#fragment',
                'https://ssl-proxy-for-https.example.com',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX#fragment',
                patched,
                )
    
    def test_url_patcher_6(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org:8081/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com',
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org:8081/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_url_patcher_7(self):
        patched = torrent_proxy_patcher.url_patcher(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                None,
                )
        
        self.assertIsInstance(patched, str)
        self.assertEqual(
                'http://bt3.rutracker.org/ann?uk=XXXXXXXX',
                patched,
                )
    
    def test_check_patched(self):
        self.assertTrue(torrent_proxy_patcher.check_patched(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com',
                ))
    
    def test_check_patched_2(self):
        self.assertFalse(torrent_proxy_patcher.check_patched(
                'https://ssl-proxy-for-https.example.com.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com',
                ))
    
    def test_check_patched_3(self):
        self.assertTrue(torrent_proxy_patcher.check_patched(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                'https://ssl-proxy-for-https.example.com/',
                ))
    
    def test_check_patched_4(self):
        self.assertFalse(torrent_proxy_patcher.check_patched(
                'https://ssl-proxy-for-https.example.com/bt3.rutracker.org/ann?uk=XXXXXXXX',
                None,
                ))
