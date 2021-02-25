'''
Author: your name
Date: 2020-12-08 14:49:13
LastEditTime: 2020-12-09 13:58:41
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/focusDetect/module/1.py
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

from nebula2.Config import Config
from nebula2.net import ConnectionPool

from utils.FormatResp import print_resp

def nebulapool(config_env):
    # define a config
    config = Config()
    config.max_connection_pool_size = 10
    # init connection pool
    connection_pool = ConnectionPool()
    # if the given servers are ok, return true, else return false
    ok = connection_pool.init([(config_env["nebula_ip"], config_env["nebula_port"])], config)
    assert ok
    # get session from the pool
    return connection_pool

    session = connection_pool.get_session(config_env["nebula_user"], config_env["nebula_passwd"])

    
    # show hosts
    
    resp = session.execute("USE focus_detect;")
    assert resp.is_succeeded(), resp.error_msg()
    
    ip = "2.2.2.2"
    sql = """insert vertex asset(ip) values "{}":("{}");""".format(ip, ip)
    resp  = session.execute(sql)
    assert resp.is_succeeded(), resp.error_msg()
    
    # for item in resp:
    #     # print(item)
    #     for value in item:
    #         print(value)
    
    # release session
    # session.release()
    
    # close the pool
    # connection_pool.close()