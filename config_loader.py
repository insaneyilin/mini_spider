#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: config_loader.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

import ConfigParser
import logging

class ConfigLoader(object):
    """
    This class is used to load config file.

    Attributes:
        file_path: config file path.
        configs: config dict
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.configs = {}


    def initialize(self):
        """
        load configs from config file
        """
        config_parser = ConfigParser.ConfigParser()
        try:
            conf_res = config_parser.read(self.file_path)
        except ConfigParser.MissingSectionHeaderError as e:
            logging.error('CONFIG ERROR: %s' % e)
            return False
        except Exception as e:
            logging.error('CONFIG ERROR: %s' % e)
            return False

        if len(conf_res) == 0:
            return False
        try:
            self.configs['url_list_file'] = config_parser.get('spider', 'url_list_file').strip()
            self.configs['output_directory'] = config_parser.get('spider', 'output_directory').strip()
            self.configs['max_depth'] = config_parser.getint('spider', 'max_depth')
            self.configs['crawl_timeout'] = config_parser.getfloat('spider', 'crawl_timeout')
            self.configs['crawl_interval'] = config_parser.getfloat('spider', 'crawl_interval')
            self.configs['target_url'] = config_parser.get('spider', 'target_url').strip()
            self.configs['thread_count'] = config_parser.getint('spider', 'thread_count')
            self.configs['try_times'] = config_parser.getint('spider', 'try_times')
            self.configs['tag_dict'] = {'a':'href', 'img':'src', 'link':'href', 'script':'src'}
        except ConfigParser.NoSectionError as e:
            logging.error('CONFIG ERROR: No section: \'spider\', %s' % e)
            return False
        except ConfigParser.NoOptionError as e:
            logging.error('CONFIG ERROR: No option, %s' % e)
            return False
        return True


    def get_url_list_file(self):
        """
        get path of 'seeds-url' file
        """
        return self.configs['url_list_file']


    def get_output_dir(self):
        """
        get output-dir for storing pages
        """
        return self.configs['output_directory']


    def get_max_depth(self):
        """
        get max-depth of breadth-first crawling
        """
        return self.configs['max_depth']


    def get_crawl_timeout(self):
        """
        get downloadings-timeout
        """
        return self.configs['crawl_timeout']


    def get_crawl_interval(self):
        """
        get time-interval between downloadings
        """
        return self.configs['crawl_interval']


    def get_target_url(self):
        """
        get pattern of target_url
        """
        return self.configs['target_url']


    def get_thread_count(self):
        """
        get thread-count for minispider
        """
        return self.configs['thread_count']


    def get_try_times(self):
        """
        get attempt times for downloading a web-page
        """
        return self.configs['try_times']


    def get_tag_dict(self):
        """
        get pic flag for Url-object
        """
        return self.configs['tag_dict']
