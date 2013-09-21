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

import sys
from os import path
import argparse
import configparser
import threading
import traceback
from .bdecode import bdecode
from .bencode import bencode
from .torrent_proxy_patcher import torrent_proxy_patcher

DEFAULT_CONFIG_PATH = path.abspath(path.join(
        path.dirname(__file__),
        '..',
        'torrent-proxy-patcher.cfg',
        ))

def main():
    arg_parser = argparse.ArgumentParser(
            description='utility for batch changing tracker-URL in torrent-files to proxy-URL',
            )
    
    arg_parser.add_argument(
            '--config',
            metavar='CONFIG-PATH',
            help='path to config file. default is {!r}'.format(DEFAULT_CONFIG_PATH),
            )
    
    arg_parser.add_argument(
            '--verbose',
            action='store_true',
            help='be more verbose. WARNING: it is dangerous, because URL may has secret key',
            )
    
    arg_parser.add_argument(
            '--force',
            action='store_true',
            help='disable poka-yoke',
            )
    
    arg_parser.add_argument(
            'torrent_file',
            nargs='+',
            metavar='TORRENT-FILE-PATH',
            help='path to .torrent file',
            )
    
    args = arg_parser.parse_args()
    
    config_path = args.config
    
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    config = configparser.ConfigParser()
    with open(config_path, encoding='utf-8', errors='replace') as config_fd:
        config.read_file(config_fd, source=config_path)
    
    proxy_for_http = config.get('torrent-proxy-patcher', 'proxy-for-http', fallback=None)
    proxy_for_https = config.get('torrent-proxy-patcher', 'proxy-for-https', fallback=None)
    replace_mode = config.getboolean('torrent-proxy-patcher', 'replace-mode', fallback=None)
    
    def task_thread_func():
        # perform task not in main thread
        
        for torrent_path in args.torrent_file:
            try:
                if not args.force:
                    if not torrent_path.endswith('.torrent'):
                        print(
                                'error: file {!r} may be is not a torrent file'.format(torrent_path),
                                file=sys.stderr,
                                )
                        
                        continue
                
                with open(torrent_path, mode='rb') as fd:
                    torrent_data = bdecode(fd.read())
                
                if args.verbose:
                    print('file {!r}:'.format(torrent_path))
                    def on_url_patched(url, new_url):
                        assert isinstance(url, str)
                        assert isinstance(new_url, str)
                        
                        print('announce url: {!r} to {!r}'.format(url, new_url))
                else:
                    def on_url_patched(url, new_url):
                        pass
                
                torrent_proxy_patcher(
                        torrent_data,
                        proxy_for_http=proxy_for_http,
                        proxy_for_https=proxy_for_https,
                        on_url_patched=on_url_patched,
                        replace_mode=replace_mode,
                        )
                
                with open(torrent_path, mode='wb') as fd:
                    fd.write(bencode(torrent_data))
            except:
                print(
                        'error: file {!r}:\n'.format(torrent_path) +
                                traceback.format_exc().strip(),
                        file=sys.stderr,
                        )
    
    task_thread = threading.Thread(target=task_thread_func)
    task_thread.start()
    task_thread.join()
