'''
Author: sdc
Date: 2020-11-26 11:26:22
LastEditTime: 2020-12-09 15:51:33
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/relate/module/loop.py
'''

#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-
# __author__: sdc

import os
import sys
import json

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

from module.kafkaConsume import regCallback

'''
description: 回调函数
param   message     接收到的单条异常事件消息  json结构
return  True/False  消息处理状态
'''
def callback(message):
    # print(message)
    return True


'''
description: 注册KAFKA回调函数，流式处理数据（阻塞式）
param1   回调函数
param2   功能模块名称
'''
regCallback(callback, "hoop")
