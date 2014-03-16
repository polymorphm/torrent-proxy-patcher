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

import sys
import os, os.path
import argparse
import configparser
import threading
import traceback
from .flock import flock_context
from .bdecode import bdecode
from .bencode import bencode
from .torrent_proxy_patcher import torrent_proxy_patcher

DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
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
                if not torrent_path.endswith('.torrent') and not args.force:
                    print(
                            'error: file {!r} may be is not a torrent file'.format(torrent_path),
                            file=sys.stderr,
                            )
                    
                    continue
                
                with flock_context(torrent_path):
                    with open(torrent_path, mode='rb') as fd:
                        torrent_data = bdecode(fd.read())
                    
                    if args.verbose:
                        print('file {!r}...'.format(torrent_path))
                        def on_url_patched(url, new_url):
                            assert isinstance(url, str)
                            assert isinstance(new_url, str)
                            
                            print('announce url: {!r} => {!r}'.format(url, new_url))
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
                    
                    torrent_new_path = '{}.new-{}'.format(torrent_path, os.getpid())
                    with open(torrent_new_path, mode='wb') as fd:
                        fd.write(bencode(torrent_data))
                    os.replace(torrent_new_path, torrent_path)
            except:
                print(
                        'error: file {!r}:\n'.format(torrent_path) +
                                traceback.format_exc().strip(),
                        file=sys.stderr,
                        )
    
    task_thread = threading.Thread(target=task_thread_func)
    task_thread.start()
    task_thread.join()
