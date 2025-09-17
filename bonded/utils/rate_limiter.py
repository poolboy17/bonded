"""
Rate limiter for API calls with concurrency control
"""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Async rate limiter with concurrent request limiting"""
    
    def __init__(self, requests_per_minute: int = 100, max_concurrent: int = 5):
        self.requests_per_minute = requests_per_minute
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.request_times = []
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.semaphore.acquire()
        await self._wait_if_needed()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.semaphore.release()
    
    async def _wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        async with self._lock:
            current_time = time.time()
            
            # Remove requests older than 1 minute
            cutoff_time = current_time - 60
            self.request_times = [t for t in self.request_times if t > cutoff_time]
            
            # Check if we need to wait
            if len(self.request_times) >= self.requests_per_minute:
                # Wait until the oldest request is more than 1 minute old
                wait_time = 60 - (current_time - self.request_times[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Remove the old request
                    self.request_times.pop(0)
            
            # Record this request
            self.request_times.append(current_time)
    
    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
        current_time = time.time()
        cutoff_time = current_time - 60
        recent_requests = [t for t in self.request_times if t > cutoff_time]
        
        return {
            'requests_last_minute': len(recent_requests),
            'requests_per_minute_limit': self.requests_per_minute,
            'max_concurrent': self.max_concurrent,
            'available_slots': self.semaphore._value
        }