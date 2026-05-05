import threading
from datetime import datetime

def trace(action, component="APP"):
    """Prints a timestamped, thread-aware debug log."""
    t_name = threading.current_thread().name
    if t_name == "MainThread":
        t_name = "MAIN"
    t_stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{t_stamp}] [{t_name}] [{component}] {action}")
