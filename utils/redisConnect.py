'''
Author: sdc
Date: 2020-11-26 11:54:33
LastEditTime: 2020-11-30 16:53:51
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/relate/utils/redisConnect.py
'''

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__: sdc

import os
import sys

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

import redis

'''
@description:  初始化redis连接池对象
@param  conf(dict)
@return:  redis_conn(object)
'''
def redispool(config_env):
    # 开启redis连接池
    redis_pool = redis.ConnectionPool(
                                        host=config_env["redis_ip"],
                                        port=config_env["redis_port"],
                                        db=config_env["redis_db"],
                                        password=config_env["redis_passwd"],
                                        decode_responses=True
    )
    redis_conn = redis.Redis(connection_pool=redis_pool)
    return redis_conn
