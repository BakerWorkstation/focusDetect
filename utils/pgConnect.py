'''
Author: sdc
Date: 2020-11-26 11:53:33
LastEditTime: 2020-11-30 16:53:33
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/relate/utils/pgConnect.py
'''

#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-
# __author__: sdc

import os
import sys

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

import redis
import psycopg2
from DBUtils.PooledDB import PooledDB


'''
@description:  初始化pg连接池对象
@param  conf(dict)
@return:  pg_conn(object)
'''
def pgpool(config_env): 
    try:
        # 开启pg连接池
        pg_pool = PooledDB(
                            psycopg2,
                            1,
                            database=config_env["pg_db"],
                            user=config_env["pg_user"],
                            password=config_env["pg_passwd"], 
                            host=config_env["pg_host"],
                            port=config_env["pg_port"]
        )
    except psycopg2.OperationalError as e:
        print("Error: threatsConsume function pg connect fail-> message: %s" % str(e))
        sys.exit(0)
    pg_conn = pg_pool.connection()
    return pg_conn
