#!/usr/bin/python3
# -*- coding: utf-8 -*- 
# --author：valecalida--
from scapy.layers.inet import IP, ICMP, sr1
from random import randint
from ipaddress import ip_network
from threading import Thread
import time
 
 
def ping_single(ip):
    ip_id = randint(1, 65535)
    icmp_id = randint(1, 65535)
    icmp_seq = randint(1, 65535)
    packet = IP(dst=ip, ttl=64, id=ip_id)/ICMP(id=icmp_id, seq=icmp_seq)
    response = sr1(packet, timeout=1, verbose=0)
    if response:
        print("[+] %s is alive" % str(ip))
 
 
def ping_scan(network):
    ip_list = ip_network(network, False)
    for ip in ip_list:
        t = Thread(target=ping_single, args=[str(ip)])
        t.start()
 
 
if __name__ == '__main__':
 
    host = '10.255.175.0/24'
    t1 = time.time()
    ping_scan(host)
    t2 = time.time()
    print("[+] 本次扫描共花费 %s 秒" % (t2 - t1))
