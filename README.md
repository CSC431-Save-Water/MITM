# MITM & DDoS Demonstration

School project demonstrating Man-in-the-Middle and DDoS attacks against a simple Java HTTP server in a controlled VM environment.

## Network Setup

| Machine | IP | Role |
|---------|-----|------|
| Server | `10.0.101.71` | Runs `SimpleWebServer.java` on port 8000 |
| Victim | `10.0.101.64` | Browser client |
| Attacker | (your VM) | Runs attack scripts |

All three machines must be on the same `10.0.101.x` subnet. To change IPs, edit `config.py`.

## Configuration

All settings live in one file — `config.py`:

```python
VICTIM_IP = "10.0.101.64"
SERVER_IP = "10.0.101.71"
INTERFACE = "eth0"         # Run "ip a" to find yours
PROXY_PORT = 8080
TARGET_PORT = 8000
FAKE_PAGE = "fake_index.html"
```

## 1. Start the Server

On the server machine (`10.0.101.71`):

```bash
javac SimpleWebServer.java
java SimpleWebServer
```

Verify it works by browsing to `http://10.0.101.71:8000` from the victim.

## 2. DDoS Attack

Floods the server with HTTP requests and uses Slowloris to hold connections open. The Java server is single-threaded (`setExecutor(null)`), so Slowloris alone can block all legitimate traffic.

**On the attacker machine:**

```bash
pip3 install scapy       # only needed for MITM, not DDoS
python3 ddos.py
```

Press `Ctrl+C` to stop.

**How it works:**
- **HTTP Flood** (200 threads) — blasts rapid GET requests using raw sockets
- **Slowloris** (150 connections) — opens connections and sends partial HTTP headers slowly, never completing the request, so the server thread hangs waiting for the rest

**Verify it's working:** While `ddos.py` is running, try loading `http://10.0.101.71:8000` from the victim browser. It should time out or fail to load.

## 3. MITM Attack (No Sudo)

Runs a reverse proxy on the attacker that intercepts HTTP traffic and replaces the server's response with a fake page.

**On the attacker machine:**

```bash
python3 mitm_proxy.py
```

**On the victim:** Browse to `http://<attacker_ip>:9000` instead of the real server. The proxy fetches from the real server but serves `fake_index.html` — a dark page with a skull, "YOU HAVE BEEN INTERCEPTED" message, and a fake "DOWNLOAD SECURITY UPDATE" button that does nothing.

## 4. MITM Attack (With Sudo — ARP Spoofing)

This is the "real" MITM where the victim doesn't know traffic is being intercepted. Requires root on the attacker.

**Terminal 1 — Network setup:**
```bash
sudo ./setup_mitm.sh
```

**Terminal 2 — HTTP interceptor:**
```bash
python3 http_interceptor.py
```

**Terminal 3 — ARP spoofing:**
```bash
sudo python3 arp_spoof.py
```

**On the victim:** Browse to `http://10.0.101.71:8000` normally — the attacker intercepts and replaces the page.

**Cleanup:**
```bash
sudo ./cleanup_mitm.sh
```

## 5. MITM Malware Injection (mitmproxy)

Uses `mitmproxy` to inject a fake "Click Here for Free Prize!" button into the real HTML response.

```bash
pip3 install mitmproxy
mitmproxy -s inject_malware.py --mode transparent
```

## Files

| File | Description |
|------|-------------|
| `config.py` | All IPs, ports, and settings — edit this one file |
| `SimpleWebServer.java` | Target Java HTTP server (port 8000) |
| `index.html` | Legitimate page served by the Java server |
| `ddos.py` | DDoS attack — HTTP flood + Slowloris |
| `mitm_proxy.py` | MITM reverse proxy (no sudo required) |
| `arp_spoof.py` | ARP cache poisoning (requires sudo) |
| `http_interceptor.py` | HTTP interceptor for ARP-based MITM |
| `inject_malware.py` | mitmproxy script to inject malicious button |
| `fake_index.html` | Fake page served during MITM |
| `setup_mitm.sh` | Enables IP forwarding + iptables redirect |
| `cleanup_mitm.sh` | Reverses network changes |
