#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: downloader.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

import ssl
import urllib2
import socket
import logging

class Downloader(object):
    """
    Download url_object's HTML source

    Attributes：
        url_obj
        try_times
        timeout
    """
    def __init__(self, url_obj, timeout, try_times=3):
        self.url_obj = url_obj
        self.timeout = timeout
        self.try_times = try_times

    def run(self):
        """
        检查 url_obj 是否可以被访问

        Returns:
            response 对象/None: URL 访问成功/URL 访问失败
            0/-1 : 访问成功与失败
        """
        for i in range(self.try_times):
            try:
                context = ssl._create_unverified_context()
                response = urllib2.urlopen(self.url_obj.get_url(), timeout=self.timeout,
                                           context=context)
                response.depth = self.url_obj.get_depth()
                return (response, 0)

            except urllib2.URLError as e:
                if i == self.try_times - 1:
                    error_info = \
                        '* Downloading failed : %s-%s' % (self.url_obj.get_url(), e)

            except UnicodeEncodeError as e:
                if i == self.try_times - 1:
                    error_info = \
                        '* Downloading failed : %s-%s' % (self.url_obj.get_url(), e)

            except urllib2.HTTPError as e:
                if i == self.try_times - 1:
                    error_info = \
                        '* Downloading failed : %s-%S' % (self.url_obj.get_url(), e)

            except socket.timeout as e:
                if i == self.try_times - 1:
                    error_info = \
                        '* Downloading failed : %s - %s' % (self.url_obj.get_url(), e)

            except Exception as e:
                if i == self.try_times - 1:
                    error_info = \
                        '* Downloading failed : %s - %s' % (self.url_obj.get_url(), e)

            logging.warn(' * Try for {}th times'.format(i + 1))
            if i == self.try_times - 1:
                logging.warn(error_info)
                return (None, -1)
