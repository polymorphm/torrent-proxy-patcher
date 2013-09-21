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

from urllib import parse as url_parse

RETRACKER_LOCAL_URL = 'http://retracker.local/announce'

def normalize_proxy_url(proxy_url):
    assert proxy_url is not None
    
    proxy_scheme, proxy_netloc, proxy_path, proxy_query, proxy_fragment = url_parse.urlsplit(proxy_url)
    
    if not proxy_path.endswith('/'):
        proxy_path = proxy_path + '/'
    
    proxy_url = proxy_scheme + '://' + proxy_netloc + proxy_path
    
    return proxy_url

def check_patched(url, proxy_url):
    if proxy_url is None:
        return False
    
    proxy_url = normalize_proxy_url(proxy_url)
    
    if url.startswith(proxy_url):
        return True
    
    return False

def url_patcher(url, proxy_url):
    assert isinstance(url, str)
    assert isinstance(proxy_url, str)
    
    proxy_url = normalize_proxy_url(proxy_url)
    orig_scheme, orig_netloc, orig_path, orig_query, orig_fragment = url_parse.urlsplit(url)
    
    if orig_query:
        orig_query = '?' + orig_query
    
    if orig_fragment:
        orig_fragment = '#' + orig_fragment
    
    new_url = proxy_url + orig_netloc + orig_path + orig_query + orig_fragment
    
    return new_url

def read_announce_list_list(torrent_data):
    # read as editable list
    
    assert torrent_data is not None
    
    announce_list_list = []
    
    single_announce = torrent_data.get(b'announce')
    
    if isinstance(single_announce, (bytes, str)):
        if isinstance(single_announce, bytes):
            single_announce = single_announce.decode(errors='replace')
        
        if single_announce:
            announce_list_list = [[single_announce]]
    
    raw_announce_list_list = torrent_data.get(b'announce-list')
    
    if isinstance(raw_announce_list_list, (tuple, list)):
        new_announce_list_list = []
        
        for raw_announce_list in raw_announce_list_list:
            if not isinstance(raw_announce_list, (tuple, list)):
                continue
            
            announce_list = []
            
            for announce_item in raw_announce_list:
                if not isinstance(announce_item, (bytes, str)):
                    continue
                
                if isinstance(announce_item, bytes):
                    announce_item = announce_item.decode(errors='replace')
                
                if announce_item:
                    announce_list.append(announce_item)
            
            if announce_list:
                new_announce_list_list.append(announce_list)
        
        if new_announce_list_list:
            # if ``new_announce_list_list`` exist
            #       than ``single_announce`` is not needed
            
            announce_list_list = new_announce_list_list
    
    return announce_list_list

def write_announce_list_list(torrent_data, announce_list_list):
    assert torrent_data is not None
    assert announce_list_list is not None
    
    if not announce_list_list:
        torrent_data[b'announce'] = b''
        torrent_data[b'announce-list'] = (),
        return
    
    torrent_data[b'announce'] = announce_list_list[0][0]
    torrent_data[b'announce-list'] = \
            tuple(tuple(announce_list) for announce_list in announce_list_list)

def torrent_proxy_patcher(
        torrent_data,
        proxy_for_http=None,
        proxy_for_https=None,
        on_url_patched=None,
        replace_mode=None,
        ):
    if not isinstance(torrent_data, dict):
        raise ValueError('invalid torrent data format')
    
    if replace_mode is None:
        replace_mode = False
    
    def check_patched_all(announce):
        if check_patched(announce, proxy_for_http) or \
                check_patched(announce, proxy_for_https):
            return True
        
        return False
    
    announce_list_list = read_announce_list_list(torrent_data)
    patched_announce_list_total = [] # this var -- need only for: detect copies of patched url
    patched_announce_list_list = []
    
    for announce_list in announce_list_list:
        patched_announce_list = []
        
        for announce in announce_list:
            if check_patched_all(announce):
                if replace_mode and announce:
                    # in replace mode -- we need save old patched urls
                    
                    patched_announce_list.append(announce)
                
                patched_announce_list_total.append(announce)
                
                continue
            
            if RETRACKER_LOCAL_URL == announce:
                continue
            
            if announce.startswith('http:'):
                if proxy_for_http is None:
                    continue
                
                new_announce = url_patcher(announce, proxy_for_http)
            elif announce.startswith('https:'):
                if proxy_for_https is None:
                    continue
                
                new_announce = url_patcher(announce, proxy_for_https)
            else:
                continue
            
            if new_announce in patched_announce_list_total:
                # copies of patched url -- avoid
                continue
            
            if on_url_patched is not None:
                on_url_patched(announce, new_announce)
            
            if new_announce:
                patched_announce_list.append(new_announce)
                patched_announce_list_total.append(new_announce)
        
        if patched_announce_list:
            patched_announce_list_list.append(patched_announce_list)
    
    if replace_mode:
        # replace mode
        
        announce_list_list = patched_announce_list_list
    else:
        # add mode
        
        announce_list_list = patched_announce_list_list + announce_list_list
    
    write_announce_list_list(torrent_data, announce_list_list)
