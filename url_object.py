#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: url_object.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

class Url(object):
    """
    This class is used to represent a url(address + depth)

    Attributes:
        url   : string of url 
        depth : depth of the url
    """

    def __init__(self, url, depth=0):
    	# Python 中的约定：
    	#   以单下划线开头的表示的是 protected 类型的变量
    	#   以双下划线开头的表示的是私有类型的变量
        self.__url = url
        self.__depth = depth


    def get_url(self):
        """
        get url address
        """
        return self.__url


    def get_depth(self):
        """
        get url depth
        """
        return self.__depth
