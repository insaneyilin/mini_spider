#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: log.py
Author: guiyilin(yilin.gui@gmail.com)
Date: 2020-11-02 23:41:00
"""

import os
import logging
import logging.handlers

def init_log(log_path, level=logging.INFO, when="D", backup=7,
             format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
             datefmt="%m-%d %H:%M:%S"):
    """
    init_log - initialize logging module

    Args:
        log_path: Log file path prefix.
                Log data will be writeen into log_path.log.
                Any non-exist parent directories will be created automatically
        level: Log message above the level will be saved.
                DEBUG < INFO < WARNING < ERROR < CRITICAL
                The default value is logging.INFO
        when: how to split the log file by time interval
                    'S' : Seconds
                    'M' : Minutes
                    'H' : Hours
                    'D' : Days
                    'W' : Week day
                    default value: 'D'
        format: Format of the log.
                Default format:
                    %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                    e.g. INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
        backup: how many backup file to keep
                    default value: 7

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger()
    logger.setLevel(level)

    log_path_dirname = os.path.dirname(log_path)
    if not os.path.isdir(log_path_dirname):
        os.makedirs(log_path_dirname)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
