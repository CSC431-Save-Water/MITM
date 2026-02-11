#!/bin/bash
# ============================================================
# MITM Cleanup Script - Reverses all changes made by setup
# ============================================================

if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root (sudo)."
    exit 1
fi

echo "[*] Cleaning up MITM setup..."

echo "[1/2] Flushing iptables NAT rules..."
iptables -t nat -F
echo "      Done."

echo "[2/2] Disabling IP forwarding..."
echo 0 > /proc/sys/net/ipv4/ip_forward
echo "      Done."

echo "[+] Cleanup complete. Network is restored to normal."
