#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: crawl_thread.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

import threading
import logging
import urllib
import re
import time
import os

import html_parser
import downloader

class CrawlerThread(threading.Thread):
    """
    This class is a crawler thread for crawling pages by BFS

    Attributes:
        process_request : request callback
        process_response: response callback
        output_dir      : 存放爬取页面的目录
        crawl_interval  : 爬取间隔
        crawl_timeout   : 爬取时间延迟
        target_url      : 目标文件链接格式
        max_depth       : 爬取最大深度
        tag_dict        : 链接标签字典
    """
    def __init__(self, name, process_request, process_response, args_dict):
        super(CrawlerThread, self).__init__(name=name)
        self.process_request = process_request
        self.process_response = process_response
        self.output_dir = args_dict['output_dir']
        self.crawl_interval = args_dict['crawl_interval']
        self.crawl_timeout = args_dict['crawl_timeout']
        self.url_pattern = args_dict['url_pattern']
        self.max_depth = args_dict['max_depth']
        self.tag_dict = args_dict['tag_dict']


    def run(self):
        """
        线程工作函数
        """
        while 1:
            url_obj = self.process_request()
            time.sleep(self.crawl_interval)

            logging.info('%-12s  : get a url in depth: ' %
                         threading.currentThread().getName() + str(url_obj.get_depth()))

            # flag = 0 表示正常下载，-1 表示下载失败，2 表示 > max_depth 
            if self.is_target_url(url_obj.get_url()):
                flag = -1
                if self.save_target_url_page(url_obj.get_url()):
                    flag = 1
                self.process_response(url_obj, flag)
                continue

            if url_obj.get_depth() < self.max_depth:
                downloader_inst = downloader.Downloader(url_obj, self.crawl_timeout)
                response, flag = downloader_inst.run()  # flag = 0 or -1

                if flag == -1:  # download failed
                    self.process_response(url_obj, flag)
                    continue

                if flag == 0:  # download sucess
                    content = response.read()
                    url = url_obj.get_url()
                    soup = html_parser.HtmlParser(content, self.tag_dict, url)
                    extract_url_list = soup.extract_url()

                    self.process_response(url_obj, flag, extract_url_list)
            else:
                flag = 2  # depth > max_depth 的正常URL
                self.process_response(url_obj, flag)


    def is_target_url(self, url):
        """
        判断 url 是否符合 target_url 的形式

        Args:
            url: 输入 url

        Returns:
            True/False: 符合返回 True，否则返回 False
        """
        return True if self.url_pattern.match(url) else False


    def save_target_url_page(self, url):
        """
        save target_url page into output_dir

        Args:
            url: 输入 url

        Returns:
            none
        """
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        file_name = urllib.quote_plus(url)
        if len(file_name) > 127:
            file_name = file_name[-127:]
        target_path = "{}/{}".format(self.output_dir, file_name)
        try:
            urllib.urlretrieve(url, target_path)
            return True
        except IOError as e:
            logging.warn(' * Save target Faild: %s - %s' % (url, e))
            return False