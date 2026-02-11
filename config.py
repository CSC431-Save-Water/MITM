# ============================================================
# MITM Configuration - Change these values to match your setup
# ============================================================

VICTIM_IP = "10.0.101.64"
SERVER_IP = "10.0.101.71"
INTERFACE = "eth0"         # Network interface (use "ip a" to find yours)
PROXY_PORT = 8080          # Port the interceptor listens on
TARGET_PORT = 8000         # Port the real server runs on
FAKE_PAGE = "fake_index.html"
