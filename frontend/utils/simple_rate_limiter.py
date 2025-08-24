"""
Simple rate limiter that actually works for low RPM values
"""
import time
import threading

class SimpleRateLimiter:
    """Simple rate limiter that enforces requests per second properly"""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def apply_rate_limiting(self):
        if self.requests_per_second <= 0:
            return
            
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                print(f"🔄 Rate limiting: sleeping {sleep_time:.2f}s (RPS: {self.requests_per_second})")
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
