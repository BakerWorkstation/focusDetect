'''
Author: sdc
Date: 2020-11-27 16:48:55
LastEditTime: 2021-01-22 10:34:22
LastEditors: Please set LastEditors
Description: 从KAFKA手动方式拉取数据，多线程平均分配多分区消费方式
FilePath: /opt/relate/module/kafkaConsume.py
'''

#!/usr/bin/env python3.6
# -*- coding:utf-8 -*-
# __author__: sdc


import os
import sys
import json
import time
import datetime
import threading
from multiprocessing import Process
from struct import unpack
from socket import AF_INET, inet_pton, inet_aton


workpath = os.path.split(os.path.realpath(__file__))[0]+"/../"
sys.path.insert(0, workpath)
sys.path.append(os.path.join(workpath, "./env/linux/"))

from confluent_kafka import Consumer, Producer, TopicPartition, admin

from utils.log import record
from utils.redisConnect import redispool
from utils.nebulaConnect import nebulapool

# 从loadConf.py中加载进程环境变量
from utils import loadConf; loadConf._init()
config = loadConf.get_value()
tmpdict = {}
# main_thread_lock = threading.Lock()

class ConsumeData(object):
    
    def __init__(self) -> None:
        self.broker_list = "%s:%s" % (config["kafka_ip"], config["kafka_port"])
        self.kafka_pro_conf = {
            'bootstrap.servers': self.broker_list,
            'message.max.bytes': 10485760,
            'retries':3,
            'socket.send.buffer.bytes':10000000,
            'enable.idempotence':True
        }
        self.kafka_consume_conf = {
            'bootstrap.servers': self.broker_list,
            'enable.auto.commit': False,
            'max.poll.interval.ms': config["kafka_max_poll"],
            'default.topic.config': {'auto.offset.reset': config["kafka_reset"]}
        }


    def getPartition(self, topicname) -> int:
        """
        description:  获取KAFKA话题对应的分区数
        param {*} topicname 话题名称
        return {*} partitions_num  话题对应分区数
        """
        object=admin.AdminClient(self.kafka_pro_conf)
        data=object.list_topics(timeout=10)
        partitions_num = len(data.topics[topicname].partitions)
        return partitions_num


    def delivery_report(self, err, msg) -> None:
        """
        description:    kafka生产者回调函数
        param {type}    err(object),  message(string)
        Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). 
        """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


    def consumeData(self, topic, partition, callback, redis_conn, nebula_session, logger, elogger, group_id=config["kafka_group_id"]) -> None:
        """
        description:    kafka消费者处理数据函数
        param {type}    partition(int),  callback(object),  redis_conn(object), group_id(string)
        """
        offsetkey = "%s_%s_%s" % (group_id, topic, partition)
        redis_offset = redis_conn.get(offsetkey)
        broker_list = "%s:%s" % (config["kafka_ip"], config["kafka_port"])
        tp_c = TopicPartition(topic, partition, 0)
        self.kafka_consume_conf["group.id"] = group_id
        consume = Consumer(self.kafka_consume_conf)
        producer = Producer({"bootstrap.servers": broker_list})
        # 获取数据对应最小offset 与 redis记录中的offset比较
        kafka_offset = consume.get_watermark_offsets(tp_c)[0]
        if not redis_offset:
            offset = kafka_offset
        else:
            if int(redis_offset) > kafka_offset:
                offset = int(redis_offset)
            else:
                offset = kafka_offset

        # 重新绑定offset 消费
        tp_c = TopicPartition(topic, partition, offset)
        consume.assign([tp_c])
        write_offset = offset
        count = 0
        while 1:
            data = consume.consume(config["kafka_length"], timeout=2)
            if data:
                logger.info("topic: %s  partition: %s\t  data_len: %s" % (topic, partition, len(data)))
                for eachmsg in data:
                    if eachmsg.error():
                        elogger.info('error: %s, 数据指针+1 ' % eachmsg.error())
                        write_offset += 1
                        continue
                    # 处理日志数据函数   返回值 flag: True/False
                    try:
                        args = {"message": eachmsg.value(), "nebula": nebula_session, "producer": producer}
                        flag = self.caller(args, callback)
                    except:
                        flag = False

                    # 数据处理成功, 移动数据指针位置+1
                    if flag:
                        write_offset += 1

                    # with main_thread_lock:
                    #     pass
            else:
                logger.info("topic: %s  partition: %s\t无数据" % (topic, partition))
                break
            count += len(data)
            if count>=1000:
                logger.warning('分区: %s  数据达到1000 一个batch, 刷新缓冲区' % partition)
                break

        # 处理结束后， redis中更新offset
        tp_c = TopicPartition(topic, partition, write_offset)
        # 获取当前分区偏移量
        kafka_offset = consume.position([tp_c])[0].offset
        # 当前分区有消费的数据, 存在偏移量
        if kafka_offset >= 0:
            # 当redis维护的offset发成超限时，重置offset
            if write_offset > kafka_offset:
                write_offset = kafka_offset
        # print(write_offset)
        redis_conn.set(offsetkey, write_offset)
        consume.commit(offsets=[tp_c])


    def threatsConsume(self, topic, callback, module) -> None:
        """
        description:    开启多线程挂载话题分区，同时消费数据
        param {type}    topic(string),  partition(int),  config(dict)
        return:
        """
        partitions = self.getPartition(topic)
        logger = record(filename='server.log', module=module, func="kafkaData")
        elogger = record(filename='error.log', module=module, func="kafkaData")
        logger.info("准备启动工作进程")
        logger.info('Run process (%s)...' % (os.getpid()))

        # 开启redis连接池
        nebula_pool = nebulapool(config)
        nebula_session = nebula_pool.get_session(config["nebula_user"], config["nebula_passwd"])
        resp = nebula_session.execute("USE focus_detect;")
        assert resp.is_succeeded(), resp.error_msg()
        redis_conn = redispool(config)
        threads = []
        try:
            num = int(partitions / config["kafka_threads"])    #  每个线程分配的分区数
            rate = int(partitions % config["kafka_threads"])   #  是否有剩余分区没有被线程分配
            if rate:
                num += 1  # 有剩余分区，则每个线程分配的分区数+1
    
            # 子进程启动多线程方式消费当前分配的话题数据，线程数和分区数要匹配
            left = 0   #  分区区间 左边界
            right = 0  #  分区区间 右边界
            for threadId in range(config["kafka_threads"]):
                left = right
                right += num
                if right > partitions:
                    right = partitions
                if left == partitions:
                    break
                logger.info(range(left, right))
                child_thread = threading.Thread(
                                                target=self.assinPartition,
                                                args=(
                                                        topic,
                                                        range(left, right),
                                                        callback,
                                                        redis_conn,
                                                        nebula_session,
                                                        module,
                                                        logger,
                                                        elogger,
                                                ),
                                                name='LoopThread'
                )
                threads.append(child_thread)
            for eachthread in threads:
                eachthread.start()
            for eachthread in threads:
                eachthread.join()
            logger.info("exit program with 0")
        except Exception as e:
            elogger.error("Error: threatsConsume_function fail, message -> %s" % str(e))


    def assinPartition(self, topic, partitions, callback, redis_conn, nebula_session, module, logger, elogger):
        """
        description:    开启多线程对应话题分区数量，同时消费数据
        param {type}    topic(string),  partition(int),  config(dict)
        return:
        """
        while 1:
            for eachpartition in partitions:
                try:
                    self.consumeData(topic, eachpartition, callback, redis_conn, nebula_session, logger, elogger, module)
                except Exception as e:
                    elogger.error('func: consumeData error, message -> %s' % str(e))
                    time.sleep(2)


    def caller(self, input, func) -> bool:
        """
        description: 构造回调函数
        param1    消息体
        param2    回调函数
        return    True/False
        """
        return func(input)


def ptd_originlog(args):
    message = args["message"]
    producer = args["producer"]
    inttime = int(time.time())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global tmpdict
    if not tmpdict:
        tmpdict = {"ctime": inttime+600, "data": {}}
    if inttime>tmpdict["ctime"]:
        tmpdict["ctime"] = timestamp
        # print(tmpdict)
        for srcip, dstips in tmpdict["data"].items():
            # print(dstips)
            tmplist = []
            for dstip, info in dstips.items():
                count = info["count"]
                port = info["port"]
                tmplist.append("%s_%s" % (dstip, count))
                producer.produce('port_scan_detect', json.dumps({"src_ip": srcip, "dst_ip": dstip, "port": list(port), "from_date": tmpdict["stime"], "to_date": tmpdict["etime"], "detect_time": tmpdict["ctime"]}))
            producer.produce('ip_scan_detect', json.dumps({"src_ip": srcip, "dst_ip": tmplist, "from_date": tmpdict["stime"], "to_date": tmpdict["etime"], "detect_time": tmpdict["ctime"]}))
        producer.flush(timeout=10)
        del tmpdict
        tmpdict = {"ctime": inttime+600, "data": {}}
    for eachmessage in json.loads(message)["data"]:
        sip = eachmessage["src"]["ip"]
        dip = eachmessage["dst"]["ip"]
        if not (sip and dip):
            continue
        if not (check_private_addr(sip) and check_private_addr(dip)):
            continue
        if not tmpdict["data"]:
            tmpdict["stime"] = eachmessage["ts"]["start"]
        tmpdict["etime"] = eachmessage["ts"]["start"]
        # print(eachmessage["src"]["port"])
        dport = eachmessage["dst"]["port"]
        if sip not in tmpdict["data"]:
            tmpdict["data"][sip] = {}
        if dip not in tmpdict["data"][sip]:
            tmpdict["data"][sip][dip] = {"count": 0, "port": set()}
        tmpdict["data"][sip][dip]["count"] += 1
        tmpdict["data"][sip][dip]["port"].add(dport)

    return True


# ------------------------------判断ip是否为内部网络-------------------------------------
def check_private_addr(ip):
        """
        判断ip是否是内网地址，若返回True的话则为内网ip，若返回False则是外部网络ip
        """
        f = unpack('!I', inet_pton(AF_INET, ip))[0]
        '''
        下面网段可选
        '''
        private = (

            # [2130706432, 4278190080],  # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
            # [3232235520, 4294901760],  # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
            # [2886729728, 4293918720],  # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
            # [167772160, 4278190080],   # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
            [184526848, 184528895],    # 10.255.175.0,  255.255.248.0
        )  
        # for net in private:
        #     if (f & net[1]) == net[0]:
        #         return True
        for net in private:
            if f > net[0] and f < net[1]:
                return True
        return False


def port_scan(args):
    nebula_session = args["nebula"]
    message = args["message"]
    result = json.loads(message.decode())
    sip = result["src_ip"]
    dip = result["dst_ip"]
    stime = result["from_date"]
    etime = result["to_date"]
    ctime = result["detect_time"]
    ports = result["port"]

    # 插入port扫描事件顶点
    event_type = "portscan"
    eventsql = """insert vertex ipscan_detect(ctime, stime, etime, event_type) values "{}_{}":("{}", "{}", "{}", "{}");""".format(event_type, ctime, ctime, stime, etime, event_type)
    resp  = nebula_session.execute(eventsql)
    assert resp.is_succeeded(), resp.error_msg()

    for eachip in [sip, dip]:
        # 插入port扫描事件 src顶点
        basesql = """insert vertex event_asset(ip, rtime) values "{}_{}":("{}", {});"""
        ip_sql = basesql.format(event_type, eachip, eachip, int(time.time()))
        resp  = nebula_session.execute(ip_sql)
        # print(ip_sql)
        assert resp.is_succeeded(), resp.error_msg()    

        # 插入port扫描事件 src资产
        assetsql = """insert vertex asset(ip, rtime) values "{}":("{}", {});"""
        ip_sql = assetsql.format(eachip, eachip, int(time.time()))
        resp  = nebula_session.execute(ip_sql)
        assert resp.is_succeeded(), resp.error_msg()

    for port in ports:
        # 插入port扫描事件  port顶点
        print(port)
        assetsql = """insert vertex port(values) values "{}":("{}");"""
        port_sql = assetsql.format(port, port)
        resp  = nebula_session.execute(port_sql)
        assert resp.is_succeeded(), resp.error_msg()

        sql = """insert edge port_edge(count) values "{}_{}"->"{}_{}":({});""".format(event_type, ctime, event_type, sip, 1)
        print(sql)
        resp  = nebula_session.execute(sql)
        assert resp.is_succeeded(), resp.error_msg()


def ip_scan(args):
    nebula_session = args["nebula"]
    message = args["message"]
    result = json.loads(message.decode())
    sip = result["src_ip"]
    dips = result["dst_ip"]
    range = len(dips)
    stime = result["from_date"]
    etime = result["to_date"]
    ctime = result["detect_time"]

    # 插入IP扫描事件顶点
    event_type = "ipscan"
    eventsql = """insert vertex ipscan_detect(ctime, stime, etime, event_type) values "{}_{}":("{}", "{}", "{}", "{}");""".format(event_type, ctime, ctime, stime, etime, event_type)
    resp  = nebula_session.execute(eventsql)
    assert resp.is_succeeded(), resp.error_msg()

    # 插入IP扫描事件 src顶点
    basesql = """insert vertex event_asset(ip, rtime) values "{}_{}":("{}", {});"""
    sip_sql = basesql.format(event_type, sip, sip, int(time.time()))
    resp  = nebula_session.execute(sip_sql)
    # print(sip_sql)
    assert resp.is_succeeded(), resp.error_msg()    

    # 插入IP扫描事件 src资产
    assetsql = """insert vertex asset(ip, rtime) values "{}":("{}", {});"""
    sip_sql = assetsql.format(sip, sip, int(time.time()))
    resp  = nebula_session.execute(sip_sql)
    assert resp.is_succeeded(), resp.error_msg()

    # 插入IP扫描事件-> src顶点的边
    sql = """insert edge ipscan_behaviour(range_count) values "{}_{}"->"{}_{}":({});""".format(event_type, ctime, event_type, sip, range)
    print(sql)
    resp  = nebula_session.execute(sql)
    assert resp.is_succeeded(), resp.error_msg()
    for eachip in dips:
        dip = eachip.split("_")[0]
        count = int(eachip.split("_")[-1])
        # 插入IP扫描事件 dst顶点
        dip_sql = basesql.format(event_type, dip, dip, int(time.time()))
        resp  = nebula_session.execute(dip_sql)
        assert resp.is_succeeded(), resp.error_msg()
        # 插入IP扫描事件 dst资产
        dip_sql = assetsql.format(dip, dip, int(time.time()))
        resp  = nebula_session.execute(dip_sql)
        assert resp.is_succeeded(), resp.error_msg()
        # 插入IP扫描事件-> dst顶点的边
        sql = """insert edge ipscan_behaviour_verbose(access_count) values "{}_{}"->"{}_{}":({});""".format(event_type, sip, event_type, dip, count)
        # print(sql)
        resp  = nebula_session.execute(sql)
        assert resp.is_succeeded(), resp.error_msg()

    return True


def regCallback(look, module):
    """
    description:   程序入口 -> 注册KAFKA回调函数
    param1  回调函数
    param2  功能模块说明
    """
    functions = {
                "PTD_BlackData_Processed3": ptd_originlog,
                "ip_scan_detect": ip_scan,
                "port_scan_detect": port_scan
    }

    C = ConsumeData()
    #topics = ["PTD_BlackData_Processed3", "ip_scan_detect", "port_scan_detect"]
    topics = ["PTD_BlackData_Processed3", "ip_scan_detect"]
    processes = []
    # 启动多进程方式同时消费所有话题
    for eachtopic in topics:
        p = Process(target=C.threatsConsume, args=(eachtopic, functions[eachtopic], eachtopic, ))
        processes.append(p)
    for eachprocess in processes:
        eachprocess.start()
    for eachprocess in processes:
        eachprocess.join()



# if __name__ == "__main__":
#     def look(message):
#         """
#         description: 回调函数
#         param1 message
#         return True/False
#         """
#         print(message)
#         return 'success'
#     regCallback(look, "test")
