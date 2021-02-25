#!/usr/bin/python3.6
# _*_  coding=utf-8 _*_

import time
from random import randint
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def  ping_one(host):
    ip_id=randint(1,65535)
    icmp_id=randint(1,65535)
    icmp_seq=randint(1,65535)
    packet=IP(dst=host,ttl=64,id=ip_id)/ICMP(id=icmp_id,seq=icmp_seq)/b'ylp'
    ping=sr1(packet,timeout=2,verbose=False) 
    if ping:
        return 0
    else:
        return -1                

def syn_scan(hostname,lport,hport):
    ping_res=ping_one(hostname)
    if ping_res==-1:
        print('设备'+hostname+'不可达')
    else:
        #syn=IP(dst=hostname)/TCP(dport=(int(lport),int(hport)),flags=2)
        for port in range(lport, hport):
            print(port)
            syn=IP(dst=hostname)/TCP(dport=port,flags=2)
            result_raw=sr(syn,timeout=1,verbose=False)
        ##取出收到结果的数据包，做成一个清单
        #result_list=result_raw[0].res
        #for i in range(len(result_list)):
        #    #判断清单的第i个回复的接受到的数据包，并判断是否有TCP字段
        #    if(result_list[i][1].haslayer(TCP)):
        #        #得到TCP字段的头部信息
        #        TCP_Fields=result_list[i][1].getlayer(TCP).fields
        #        #判断头部信息中的flags标志是否为18(syn+ack)
        #        if TCP_Fields['flags']==18:
        #            print('端口号: '+str(TCP_Fields['sport'])+' is Open!!!')

if __name__=='__main__':
    host=input('请输入扫描主机的IP地址:')
    port_low=input('请输入扫描端口的最低端口号')
    port_high=input('请输入扫描端口的最高端口号')
    host = '10.255.175.121'
    port_low = 1
    port_high = 65535
    while 1:
        syn_scan(host,port_low,port_high) 
