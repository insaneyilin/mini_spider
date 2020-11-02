#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: test_config_loader.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

import unittest
import sys

sys.path.append('../')
import config_loader

class TestConfigLoader(unittest.TestCase):
    """
    Unit Test class of ConfigLoader
    """
    def setUp(self):
        self.conf_loader = config_loader.ConfigLoader('./spider.conf')


    def test_load_from_file_success(self):
        """
        test True for function load_from_file()
        """
        self.assertTrue(self.conf_loader.initialize())


    def test_load_from_file_fail(self):
        """
        test False for function load_from_file()
        """
        self.conf_loader.file_path = 'spider.conf_'
        self.assertFalse(self.conf_loader.initialize())


    def test_config_getters(self):
        """
        check config getters
        """
        self.assertTrue(self.conf_loader.initialize())

        self.assertEqual(self.conf_loader.get_url_list_file(), "./urls")
        self.assertEqual(self.conf_loader.get_output_dir(), "./output")
        self.assertEqual(self.conf_loader.get_max_depth(), 1)
        self.assertEqual(self.conf_loader.get_crawl_timeout(), 2)
        self.assertEqual(self.conf_loader.get_crawl_interval(), 0.5)
        self.assertEqual(self.conf_loader.get_target_url(), ".*.(gif|png|jpg|bmp)$")
        self.assertEqual(self.conf_loader.get_thread_count(), 4)
        self.assertEqual(self.conf_loader.get_try_times(), 3)


    def tearDown(self):
        self.conf_loader = None


if __name__ == '__main__':
    unittest.main()
