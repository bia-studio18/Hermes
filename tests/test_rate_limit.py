from __future__ import annotations

import asyncio

import pytest

from hermes.acquisition.rate_limit import RateLimiter


class TestRateLimiter:
    async def test_acquire_returns_zero_when_free(self):
        limiter = RateLimiter(max_requests=5, window_seconds=1.0)
        waited = await limiter.acquire()
        assert waited == 0.0

    async def test_waits_when_window_full(self):
        limiter = RateLimiter(max_requests=2, window_seconds=0.05)
        elapsed_start = asyncio.get_event_loop().time()
        await limiter.acquire()
        await limiter.acquire()
        # third acquire must wait for the window to roll
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - elapsed_start
        assert elapsed >= 0.045

    async def test_available_decreases_and_recovers(self):
        limiter = RateLimiter(max_requests=2, window_seconds=0.05)
        assert limiter.available == 2
        await limiter.acquire()
        assert limiter.available == 1
        await asyncio.sleep(0.06)
        assert limiter.available == 2

    async def test_retry_after(self):
        limiter = RateLimiter(max_requests=1, window_seconds=0.05)
        await limiter.acquire()
        assert limiter.retry_after > 0
        await asyncio.sleep(0.06)
        assert limiter.retry_after == 0.0

    async def test_context_manager_acquires_slot(self):
        limiter = RateLimiter(max_requests=1, window_seconds=10.0)
        async with limiter:
            assert limiter.available == 0

    async def test_wait_acquires_slot(self):
        limiter = RateLimiter(max_requests=1, window_seconds=0.05)
        await limiter.acquire()
        await limiter.wait()  # blocks until a slot frees
        assert limiter.available == 0
