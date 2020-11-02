#!/usr/bin/env python-2.7.3
# -*- coding: utf-8 -*-

"""
File: mini_spider.py
Description: 迷你网页爬虫，对种子链接进行广度优先抓取，并把 URL 格式符合特定 pattern 的网页保存到磁盘上
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

# 这里注意 import 的顺序要符合规范：
# * 标准库
# * 第三方库
# * 应用程序自有库

import Queue
import threading
import os
import logging
import re
import argparse

import termcolor

import url_object
import config_loader
import crawl_thread
import log

class MiniSpider(object):
    """
    This class is a crawler-master-class for operating serveral crawling threads

    Attributes:
        checking_urls      : 存放待爬取 URL 的队列
        checked_urls       : 存放已经爬取过的 URL 的队列
        error_urls         : 存放访问出错 URL 的队列
        config_file_path   : 配置文件路径
        lock               : 线程锁
    """

    def __init__(self, config_file_path='spider.conf'):
        """
        Initialize variables
        """
        self.checking_urls = Queue.Queue(0)
        self.checked_urls = set()
        self.error_urls = set()
        self.config_file_path = config_file_path
        self.lock = threading.Lock()


    def initialize(self):
        """
        Load config from file.

        Returns:
            True/False: 读取配置成功返回 True，否则返回 False
        """
        config_loader_inst = config_loader.ConfigLoader(self.config_file_path)
        conf_load_res = config_loader_inst.initialize()
        if not conf_load_res:
            self.program_end('MiniSpider Load config failed!')
            return False

        self.url_list_file = config_loader_inst.get_url_list_file()
        self.output_dir = config_loader_inst.get_output_dir()
        self.max_depth = config_loader_inst.get_max_depth()
        self.crawl_interval = config_loader_inst.get_crawl_interval()
        self.crawl_timeout = config_loader_inst.get_crawl_timeout()
        self.target_url = config_loader_inst.get_target_url()
        self.thread_count = config_loader_inst.get_thread_count()
        self.tag_dict = config_loader_inst.get_tag_dict()
        self.url_pattern = re.compile(self.target_url)  # 使用 re.complie 预先编译提升正则匹配性能

        seedfile_is_exist = self.get_seed_urls()
        return seedfile_is_exist


    def get_seed_urls(self):
        """
        get seed urls from seedUrlFile

        Returns:
            True/False : 存在种子文件返回 True, 否则返回 False
        """
        if not os.path.isfile(self.url_list_file):
            logging.error(' * seedfile does not exist!')
            self.program_end('No seedfile!')
            return False

        with open(self.url_list_file, 'rb') as f:
            lines = f.readlines()

        for line in lines:
            if line.strip() == '' or line.startswith('#'):
                continue

            url_obj = url_object.Url(line.strip(), 0)
            self.checking_urls.put(url_obj)
        return True


    def print_conf_info(self):
        """
        显示配置信息
        """
        print termcolor.colored('* MiniSpider Configurations: ', 'green')
        print termcolor.colored('* %-25s : %s' % ('url_list_file   :',
                                                   self.url_list_file),
                                                   'green'
                                                   )

        print termcolor.colored('* %-25s : %s' % ('output_directory:',
                                                   self.output_dir),
                                                   'green'
                                                   )

        print termcolor.colored('* %-25s : %s' % ('max_depth       :',
                                                  self.max_depth),
                                                  'green'
                                                  )

        print termcolor.colored('* %-25s : %s' % ('crawl_interval  :',
                                                  self.crawl_interval),
                                                  'green'
                                                  )

        print termcolor.colored('* %-25s : %s' % ('crawl_timeout   :',
                                                  self.crawl_timeout),
                                                  'green'
                                                  )

        print termcolor.colored('* %-25s : %s' % ('target_url      :',
                                                   self.target_url),
                                                   'green'
                                                   )

        print termcolor.colored('* %-25s : %s' % ('thread_count    :',
                                                  self.thread_count),
                                                  'green'
                                                  )


    def program_end(self, info):
        """
        程序退出时打印信息

        Args:
            info: 退出原因信息

        Returns:
            none
        """
        print termcolor.colored('* crawled page num : {}'.format(len(self.checked_urls)), 'green')
        logging.info('crawled  pages  num : {}'.format(len(self.checked_urls)))
        print termcolor.colored('* error page num : {}'.format(len(self.error_urls)), 'green')
        logging.info('error page num : {}'.format(len(self.error_urls)))
        print termcolor.colored('* finish_reason  :' + info, 'green')
        logging.info('reason of ending :' + info)
        print termcolor.colored('* program is ended ... ', 'green')
        logging.info('program is ended ... ')


    def run(self):
        """
        设置线程池，启动线程任务
        """
        args_dict = {}
        args_dict['output_dir'] = self.output_dir
        args_dict['crawl_interval'] = self.crawl_interval
        args_dict['crawl_timeout'] = self.crawl_timeout
        args_dict['url_pattern'] = self.url_pattern
        args_dict['max_depth'] = self.max_depth
        args_dict['tag_dict'] = self.tag_dict

        for index in xrange(self.thread_count):
            thread_name = 'thread - %d' % index
            thread = crawl_thread.CrawlerThread(thread_name,
                                                self.process_request,
                                                self.process_response,
                                                args_dict)

            thread.setDaemon(True)  # 守护进程，主线程执行完毕后会将子线程回收掉
            thread.start()
            print termcolor.colored(("Thread %s starts working ...") % index, 'yellow')
            logging.info(("Thread %s starts working ...") % index)

        # Queue.join 会在队列存在未完成任务时阻塞，等待队列无未完成任务，需要配合 Queue.task_done 使用
        self.checking_urls.join()
        self.program_end('Normal exits.')


    def is_url_visited(self, url_obj):
        """
        check whether url_obj is visited(including checked_urls and error_urls)

        Args:
            url_obj: url 对象

        Returns:
            True/False: 若访问过则返回 True ，否则返回 False
        """
        checked_url_list = self.checked_urls.union(self.error_urls)
        for checked_url in checked_url_list:
            if url_obj.get_url() == checked_url.get_url():
                return True
        return False


    def process_request(self):
        """
        线程任务 request 回调函数：
            负责从任务队列 checking_url 中取出 url 对象

        Returns:
            url_obj: 取出的 url object 对象
        """
        url_obj = self.checking_urls.get()
        return url_obj


    def process_response(self, url_obj, flag, extract_url_list=None):
        """
        线程任务 response 回调函数：
            解析 HTML 源码，获取下一层 URLs 放入 checking_urls

        Args:
            extract_url_list: 返回抽取出的urls集合
            url_obj: 被下载页面所处的url链接对象
            flag: 页面下载具体情况的返回标志
                    - 0  : 表示下载成功且为非pattern页面
                    - 1  : 表示下载成功且为符合pattern的图片
                    - -1 : 表示页面下载失败
                    - 2  : depth >= max_depth 的非 target URL
        """
        # 多个线程可能同时访问 self.checking_urls, self.checked_urls 和 self.error_urls
        # 需要加锁
        if self.lock.acquire():
            if flag == -1:
                self.error_urls.add(url_obj)

            elif flag == 0:
                self.checked_urls.add(url_obj)
                for ex_url in extract_url_list:
                    next_url_obj = url_object.Url(ex_url, int(url_obj.get_depth()) + 1)
                    if not self.is_url_visited(next_url_obj):
                        self.checking_urls.put(next_url_obj)

            elif flag == 1:
                self.checked_urls.add(url_obj)

            # Queue.task_done()函数向任务已经完成的队列发送一个信号
            # 可以理解为，每 task_done 一次，就从队列里删掉一个元素
            self.checking_urls.task_done()
        self.lock.release()


if __name__ == '__main__':
    log.init_log('./log/mini_spider')
    logging.info('%-35s' % ' * MiniSpider is starting ... ')
    red_on_cyan = lambda x: termcolor.colored(x, 'red', 'on_cyan')

    parser = argparse.ArgumentParser(description='MiniSpider')
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s 1.0.0')
    parser.add_argument('-c',
                        '--config_file',
                        action='store',
                        dest='CONF_PATH',
                        default='spider.conf',
                        help='Configuration file path')
    args = parser.parse_args()

    print red_on_cyan('* MiniSpider is Staring ... ')
    mini_spider_inst = MiniSpider(args.CONF_PATH)
    init_success = mini_spider_inst.initialize()
    if init_success:
        mini_spider_inst.print_conf_info()
        mini_spider_inst.run()

    # *********************************** end  **************************
    logging.info('%-35s' % ' * MiniSpider is ending ...')
    print red_on_cyan('* MiniSpider is ending ... ')
