"""
Simple in-memory rate limiter stub.

TODO: This is process-local and resets on restart -- fine for a single-worker
dev deployment. For production with multiple workers/instances, replace with
a shared store (e.g. Redis) or swap to `slowapi` backed by Redis.
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List

from app.config import settings


class InMemoryRateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60
        with self._lock:
            hits = [t for t in self._hits[key] if t > window_start]
            if len(hits) >= self.requests_per_minute:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


rate_limiter = InMemoryRateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
