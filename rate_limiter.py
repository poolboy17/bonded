import threading, time

class RateLimiter:
    def __init__(self, max_calls, interval):
        self.lock = threading.Lock()
        self.max = max_calls
        self.interval = interval
        self.tokens = self.max
        self.ts = time.monotonic()

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.ts
            self.tokens = min(self.max, self.tokens + elapsed * (self.max / self.interval))
            self.ts = now
            if self.tokens >= 1:
                self.tokens -= 1
                return
            wait = (1 - self.tokens) * (self.interval / self.max)
        time.sleep(wait)
        with self.lock:
            self.tokens -= 1
