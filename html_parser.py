#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: html_parser.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""
import urlparse
import logging

import bs4
import chardet

class HtmlParser(object):
    """
    This class is used to parse HTML.

    Attributes:
        content       : 待解析的html源码
        link_tag_dict : 待解析的标签
        url           : 待解析页面所处的url
    """

    def __init__(self, content, link_tag_dict, url):
        self.link_tag_dict = link_tag_dict
        self.content = content
        self.url = url


    def extract_url(self):
        """
        extract urls from html according to link_tag_dict

        Returns:
            extract_url_list : urls extracted from html
        """
        extract_url_list = []
        if not self.encode_to_utf8():
            return extract_url_list

        host_name = urlparse.urlparse(self.url).netloc
        # 使用 html5lib 解析器
        soup = bs4.BeautifulSoup(self.content, 'html5lib')

        # 检查链接标签中的元素
        for tag, attr in self.link_tag_dict.iteritems():
            all_found_tags = soup.find_all(tag)
            for found_tag in all_found_tags:
                if found_tag.has_attr(attr):
                    extract_url = found_tag.get(attr).strip()

                    if extract_url.startswith("javascript") or len(extract_url) > 256:
                        continue

                    if not (extract_url.startswith('http:') or extract_url.startswith('https:')):
                        extract_url = urlparse.urljoin(self.url, extract_url)

                    extract_url_list.append(extract_url)

        return extract_url_list


    def detect_encoding(self):
        """
        检测 self.content 文本编码

        Returns:
            encode_name/None: 检测成功返回编码名字，否则返回 None 
        """
        if isinstance(self.content, unicode):
            return 'unicode'

        try:
            encode_dict = chardet.detect(self.content)
            encode_name = encode_dict['encoding']
            return encode_name
        except Exception as e:
            logging.error(' * HtmlParserEncodingError detect_encoding: %s' % e)
            return None


    def encode_to_utf8(self):
        """
        将 self.content 的文本编码转为utf8

        Returns:
            True/False : 能正常转为utf-8则返回True，否则返回False
        """
        encoding = self.detect_encoding()
        try:
            if encoding is None:
                return False

            elif encoding.lower() == 'unicode':
                self.content = self.content.encode('utf-8')
                return True

            elif encoding.lower() == 'utf-8':
                return True

            else:
                self.content = self.content.decode(encoding, 'ignore').encode('utf-8')
                return True

        except UnicodeError as e:
            logging.warn(' * HtmlParserEncodingError - %s - %s:' % (self.url, e))
            return False

        except UnicodeEncodeError as e:
            logging.warn(' * HtmlParserEncodingError - %s - %s:' % (self.url, e))
            return False

        except UnicodeDecodeError as e:
            logging.warn(' * HtmlParserEncodingError - %s - %s:' % (self.url, e))
            return False

        except Exception as e:
            logging.warn(' * HtmlParserEncodingError - %s - %s:' % (self.url, e))
            return False
