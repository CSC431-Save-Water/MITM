import threading
import requests

# The target URL of your lab server
TARGET_URL = "http://localhost:8000/"

# Number of concurrent threads to spawn
THREADS = 50 

def send_requests():
    """Continuously sends requests to the server."""
    while True:
        try:
            # We don't even need to process the response, 
            # just making the request triggers the server's memory allocation.
            requests.get(TARGET_URL, timeout=5)
        except requests.exceptions.RequestException:
            # This will trigger once the server starts failing/dropping connections
            print("Server is no longer responding.")
            break

if __name__ == "__main__":
    print(f"Starting load simulation on {TARGET_URL}...")
    
    thread_list = []
    for i in range(THREADS):
        t = threading.Thread(target=send_requests)
        t.daemon = True # Allows script to exit easily
        thread_list.append(t)
        t.start()

    # Keep the main thread alive while workers run
    for t in thread_list:
        t.join()