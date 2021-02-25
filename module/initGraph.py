'''
Author: your name
Date: 2020-12-09 13:49:06
LastEditTime: 2021-01-22 09:46:11
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /opt/focusDetect/module/initGraph.py
'''

#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-
# __author__: sdc

import os
import sys
import json
import time

workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

# 从loadConf.py中加载进程环境变量
from utils import loadConf; loadConf._init()
config = loadConf.get_value()

from utils.nebulaConnect import nebulapool


# 开启redis连接池
nebula_pool = nebulapool(config)
nebula_session = nebula_pool.get_session(config["nebula_user"], config["nebula_passwd"])
create_space = 'CREATE SPACE `focus_detect` (partition_num = 100, replica_factor = 1, charset = utf8, collate = utf8_bin, vid_type = FIXED_STRING(100)); USE focus_detect;'
resp = nebula_session.execute(create_space)
assert resp.is_succeeded(), resp.error_msg()

# create TAG
asset = 'CREATE TAG `asset` ( `ip` string NULL, `mac` string NULL, `org` string NULL, `rtime` int64 NULL ) ttl_duration = 0, ttl_col = "";'
event_asset = 'CREATE TAG `event_asset` ( `ip` string NULL, `mac` string NULL, `org` string NULL, `rtime` int64 NULL, `try_loophole` int64 NULL DEFAULT 3, `try_process` int64 NULL DEFAULT 3, `try_syslog` int64 NULL DEFAULT 3, `try_port` int64 NULL DEFAULT 3 ) ttl_duration = 0, ttl_col = "";'
detect = 'CREATE TAG `ipscan_detect` ( `ctime` string NULL, `stime` string NULL, `etime` string NULL, `event_type` string NULL ) ttl_duration = 0, ttl_col = "";'
port = 'CREATE TAG `port` ( `values` int64 NULL, `protocol` string NULL, `flag` string NULL ) ttl_duration = 0, ttl_col = "";'
person = 'CREATE TAG `person` ( `name` string NULL, `org` string NULL, `email` string NULL, `tel` string NULL ) ttl_duration = 0, ttl_col = "";'
process = 'CREATE TAG `process` ( `name` string NULL, `params` string NULL, `path` string NULL, `pid` int64 NULL ) ttl_duration = 0, ttl_col = "";'
software = 'CREATE TAG `software` ( `name` string NULL, `path` string NULL, `version` string NULL, `pulish` string NULL, `pki` string NULL ) ttl_duration = 0, ttl_col = "";'
loophole = 'CREATE TAG `loophole` ( `number` string NULL, `type` string NULL ) ttl_duration = 0, ttl_col = "";'

# create EDGE
ip_scan = '	CREATE EDGE `ipscan_behaviour` ( `range_count` int64 NULL ) ttl_duration = 0, ttl_col = "";'
ip_scan_verbose = '	CREATE EDGE `ipscan_behaviour_verbose` ( `access_count` int64 NULL ) ttl_duration = 0, ttl_col = "";'
loophole_edge = 'CREATE EDGE `loophole_edge` ( `source` string NULL, `stime` string NULL, `etime` string NULL, `ctime` string NULL ) ttl_duration = 0, ttl_col = "";'
process_edge = 'CREATE EDGE `process_edge` ( `source` string NULL, `stime` string NULL, `etime` string NULL, `ctime` string NULL ) ttl_duration = 0, ttl_col = "";'

# create index
asset_index = 'CREATE TAG INDEX asset_index_0 on event_asset(ip(20));'
ipscan_index = 'CREATE TAG INDEX ipscan_index_0 on ipscan_detect(event_type(20), ctime(30));'

# single_person_index = ''

for eachsql in [asset, event_asset, port, person, process, software, loophole, detect, ip_scan, ip_scan_verbose, loophole_edge, process_edge, asset_index, ipscan_index]:
    resp = nebula_session.execute(eachsql)
    assert resp.is_succeeded(), resp.error_msg()

time.sleep(3)
rebuild_asset_index = 'REBUILD TAG INDEX asset_index_0;'
rebuild_ipscan_index = 'REBUILD TAG INDEX ipscan_index_0;'

for eachsql in [rebuild_asset_index, rebuild_ipscan_index]:
    resp = nebula_session.execute(eachsql)
    assert resp.is_succeeded(), resp.error_msg()

nebula_session.release()
nebula_pool.close()
