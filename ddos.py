import threading
import requests

TARGET_URL = "http://localhost:8000/"
THREADS = 100 # Increased for lab load testing

def aggressive_request():
    # Session keeps the connection open, putting more pressure on the server's state
    session = requests.Session()
    while True:
        try:
            # Short timeout prevents the script from hanging on a "stuck" server
            session.get(TARGET_URL, timeout=1)
        except requests.exceptions.RequestException:
            print("Target unreachable. Resource exhaustion likely achieved.")
            break

if __name__ == "__main__":
    print(f"Beginning high-concurrency test on {TARGET_URL}")
    for _ in range(THREADS):
        t = threading.Thread(target=aggressive_request, daemon=True)
        t.start()
    
    # Keeping the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Test stopped.")