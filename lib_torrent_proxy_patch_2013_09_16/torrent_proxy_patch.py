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

def url_patch(url, proxy_url):
    assert isinstance(url, str)
    
    if proxy_url is None:
        return url
    
    proxy_url = normalize_proxy_url(proxy_url)
    orig_scheme, orig_netloc, orig_path, orig_query, orig_fragment = url_parse.urlsplit(url)
    
    if orig_query:
        orig_query = '?' + orig_query
    
    if orig_fragment:
        orig_fragment = '#' + orig_fragment
    
    new_url = proxy_url + orig_netloc + orig_path + orig_query + orig_fragment
    
    return new_url

def torrent_proxy_patch(
        torrent_data,
        proxy_for_http=None,
        proxy_for_https=None,
        on_url_patch=None,
        ):
    if not isinstance(torrent_data, dict):
        raise ValueError('invalid torrent data format')
    
    announce = torrent_data.get(b'announce')
    
    if isinstance(announce, (bytes, str)):
        if isinstance(announce, bytes):
            announce = announce.decode(errors='replace')
        
        if announce.startswith('http:'):
            if not check_patched(announce, proxy_for_http) and \
                    not check_patched(announce, proxy_for_https):
                new_announce = url_patch(announce, proxy_for_http)
                if on_url_patch is not None:
                    on_url_patch(announce, new_announce)
                announce = new_announce
        elif announce.startswith('https:'):
            if not check_patched(announce, proxy_for_http) and \
                    not check_patched(announce, proxy_for_https):
                new_announce = url_patch(announce, proxy_for_https)
                if on_url_patch is not None:
                    on_url_patch(announce, new_announce)
                announce = new_announce
        
        torrent_data[b'announce'] = announce.encode()
    
    announce_list_list = torrent_data.get(b'announce-list')
    if isinstance(announce_list_list, (tuple, list)):
        new_announce_list_list = []
        
        for announce_list in announce_list_list:
            if not isinstance(announce_list, (tuple, list)):
                new_announce_list_list.append(announce_list)
                continue
            
            new_announce_list = []
            
            for announce_item in announce_list:
                if not isinstance(announce_item, (bytes, str)):
                    new_announce_list.append(announce_item)
                    continue
                
                if isinstance(announce_item, bytes):
                    announce_item = announce_item.decode(errors='replace')
                
                if announce_item.startswith('http:'):
                    if not check_patched(announce_item, proxy_for_http) and \
                             not check_patched(announce_item, proxy_for_https):
                        mew_announce_item = url_patch(announce_item, proxy_for_http)
                        if on_url_patch is not None:
                            on_url_patch(announce_item, new_announce_item)
                        announce_item = new_announce_item
                elif proxy_for_https is not None and announce_item.startswith('https:'):
                    if not check_patched(announce_item, proxy_for_http) and \
                             not check_patched(announce_item, proxy_for_https):
                        new_announce_item = url_patch(announce_item, proxy_for_https)
                        if on_url_patch is not None:
                            on_url_patch(announce_item, new_announce_item)
                        announce_item = new_announce_item
                
                new_announce_list.append(announce_item.encode())
            new_announce_list_list.append(tuple(new_announce_list))
        torrent_data[b'announce-list'] = tuple(new_announce_list_list)
