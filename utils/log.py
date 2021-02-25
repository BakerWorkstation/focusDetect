'''
Author: sdc
Date: 2020-11-26 10:15:36
LastEditTime: 2020-11-26 17:26:10
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/relate/utils/log.py
'''

#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-
# __author__: sdc

import os
import sys
import time
import logging
import datetime
from logging import handlers

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)

'''
@description:  创建日志句柄公共函数
@param    kwargs(dict)
@return:  log(object)
'''
def record(**kwargs):
    dirpath = os.path.join(workpath, "logs")
    func = kwargs.pop('func', None)
    module = kwargs.pop('module', None)
    if func:
        dirpath = os.path.join(dirpath, func)
    if module:
        dirpath = os.path.join(dirpath, module)
        
    try:
        os.makedirs(dirpath)
    except:
        pass
    filename = os.path.join(dirpath, kwargs['filename'])
    level = None#kwargs['level']
    datefmt = kwargs.pop('datefmt', None)
    format = kwargs.pop('format', None)
    if level is None:
        level = logging.INFO
    if datefmt is None:
        datefmt = '%Y-%m-%d %H:%M:%S'
    if format is None:
        format = '%(asctime)s [%(module)s] %(levelname)s [%(lineno)d] %(message)s'
    log = logging.getLogger(filename)
    format_str = logging.Formatter(format, datefmt)
    th = handlers.TimedRotatingFileHandler(filename=filename, backupCount=7, when='midnight', encoding='utf-8')
    #th._namer = lambda x: 'test.' + x.split[-1]
    th.setFormatter(format_str)
    th.setLevel(level)
    log.addHandler(th)
    log.setLevel(level)
    return log