from scapy.all import *
 
#首先要选择网卡的接口，就需要查看网卡接口有什么,在进行选择
#print(show_interfaces())
wifi='Realtek 8821AE Wireless LAN 802.11ac PCI-E NIC'
 
 
#模拟发包,向整个网络发包，如果有回应，则表示活跃的主机
#p=Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst='10.255.175.0/21')
p=Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst='10.255.175.5')
#ans表示收到的包的回复
print('start')
for i in range(10):
    ans,unans=srp(p,iface='eth0',timeout=10)
 
print("一共扫描到%d台主机："%len(ans))
 
#将需要的IP地址和Mac地址存放在result列表中
result=[]
for s,r in ans:
    #解析收到的包，提取出需要的IP地址和MAC地址
    result.append([r[ARP].psrc,r[ARP].hwsrc])
#将获取的信息进行排序，看起来更整齐一点
result.sort()
#打印出局域网中的主机
for ip,mac in result:
    print(ip,'------>',mac)
