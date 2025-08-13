from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RateLimiter:
    """In-memory rate limiter (fixed window via sliding deque).

    Not distributed; suitable for single-instance dev/local.
    """

    def __init__(self) -> None:
        # key -> timestamps (seconds)
        self._events: Dict[str, Deque[float]] = defaultdict(deque)
        # active SSE connections per key (e.g., ip)
        self._active_sse: Dict[str, int] = defaultdict(int)

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        dq = self._events[key]
        # purge
        cutoff = now - window_seconds
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True

    def inc_sse(self, key: str, max_concurrent: int) -> bool:
        current = self._active_sse[key]
        if current >= max_concurrent:
            return False
        self._active_sse[key] = current + 1
        return True

    def dec_sse(self, key: str) -> None:
        current = self._active_sse.get(key, 0)
        if current <= 1:
            self._active_sse.pop(key, None)
        else:
            self._active_sse[key] = current - 1


limiter = RateLimiter()


