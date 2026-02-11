#!/bin/bash
# Reverses all MITM network changes

if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root (sudo)."
    exit 1
fi

echo "[1/2] Flushing iptables NAT rules..."
iptables -t nat -F

echo "[2/2] Disabling IP forwarding..."
echo 0 > /proc/sys/net/ipv4/ip_forward

echo "[+] Cleanup complete."
