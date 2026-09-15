from __future__ import annotations

import asyncio
import logging
import time
from collections import deque

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> float:
        waited = 0.0
        async with self._lock:
            now = time.monotonic()
            self._evict(now)
            if len(self._timestamps) >= self.max_requests:
                wait_until = self._timestamps[0] + self.window_seconds
                waited = max(0.0, wait_until - now)
            else:
                waited = 0.0
        if waited > 0:
            await asyncio.sleep(waited)
            async with self._lock:
                self._evict(time.monotonic())
        self._timestamps.append(time.monotonic())
        return waited

    async def wait(self) -> None:
        await self.acquire()

    async def __aenter__(self) -> RateLimiter:
        await self.acquire()
        return self

    async def __aexit__(self, *exc: object) -> None:
        pass

    @property
    def available(self) -> int:
        now = time.monotonic()
        self._evict(now)
        return max(0, self.max_requests - len(self._timestamps))

    @property
    def retry_after(self) -> float:
        now = time.monotonic()
        self._evict(now)
        if len(self._timestamps) < self.max_requests:
            return 0.0
        return max(0.0, self._timestamps[0] + self.window_seconds - now)

    def _evict(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()
