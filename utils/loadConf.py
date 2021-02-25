'''
Author: your name
Date: 2020-11-26 09:57:11
LastEditTime: 2021-01-21 10:14:12
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/relate/utils/loadConf.py
'''

#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# __author__: sdc

import os
import sys
import json

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

import redis
import configparser

'''
@description:  配置进程中的环境变量
'''
def _init():
    global _global_dict
    try:
        conf = configparser.ConfigParser()
        conf.read(os.path.join(workpath, "conf/system.ini"))
        kafka_ip = conf.get("KAFKA", "ip")
        kafka_port = int(conf.get("KAFKA", "port"))
        kafka_threads = int(conf.get("KAFKA", "threads"))
        kafka_group_id = conf.get("KAFKA", "group_id")
        kafka_session_timeout = int(conf.get("KAFKA", "session_timeout"))
        kafka_reset = conf.get("KAFKA", "reset")
        kafka_max_poll = int(conf.get("KAFKA", "max_poll"))
        kafka_length = int(conf.get("KAFKA", "length"))
        redis_ip = conf.get("REDIS", "ip")
        redis_port = int(conf.get("REDIS", "port"))
        redis_db = int(conf.get("REDIS", "db"))
        redis_passwd = conf.get("REDIS", "password")
        nebula_ip = conf.get("NEBULA", "ip")
        nebula_port = int(conf.get("NEBULA", "port"))
        nebula_user = conf.get("NEBULA", "user")
        nebula_passwd = conf.get("NEBULA", "password")
        _global_dict = {
                        "kafka_ip": kafka_ip,
                        "kafka_port": kafka_port,
                        "kafka_threads": kafka_threads,
                        "kafka_group_id": kafka_group_id,
                        "kafka_session_timeout": kafka_session_timeout,
                        "kafka_reset": kafka_reset,
                        "kafka_max_poll": kafka_max_poll,
                        "kafka_length": kafka_length,
                        "redis_ip": redis_ip,
                        "redis_port": redis_port,
                        "redis_passwd": redis_passwd,
                        "redis_db": redis_db,
                        "nebula_ip": nebula_ip,
                        "nebula_port": nebula_port,
                        "nebula_user": nebula_user,
                        "nebula_passwd": nebula_passwd
        }
    except Exception as e:
        print(str(e))
        sys.exit()


'''
@description:  返回进程中的环境变量
@return: defValue(dict)
'''
def get_value():
    return _global_dict