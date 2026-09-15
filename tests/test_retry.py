from __future__ import annotations

import asyncio

import pytest

from hermes.acquisition.retry import RetryPolicy
from hermes.core.errors import AcquisitionError, RateLimitError, TimeoutError


class TestShouldRetry:
    def test_retryable_timeout(self):
        assert RetryPolicy().should_retry(1, TimeoutError("boom"))

    def test_retryable_rate_limit(self):
        assert RetryPolicy().should_retry(1, RateLimitError("429"))

    def test_retryable_connection_error(self):
        assert RetryPolicy().should_retry(1, ConnectionError("refused"))

    def test_not_retryable_generic_error(self):
        assert not RetryPolicy().should_retry(1, ValueError("bad input"))

    def test_exhausted_retries(self):
        policy = RetryPolicy(max_retries=2)
        assert policy.should_retry(2, TimeoutError("x")) is False

    def test_custom_retry_on_list(self):
        policy = RetryPolicy(retry_on=["ValueError"])
        assert policy.should_retry(1, ValueError("x"))
        assert not policy.should_retry(1, TypeError("x"))


class TestGetDelay:
    def test_exponential_backoff(self):
        policy = RetryPolicy(backoff_factor=1.0, max_delay=1000.0, jitter=False)
        assert policy.get_delay(1, TimeoutError()) == pytest.approx(1.0)
        assert policy.get_delay(2, TimeoutError()) == pytest.approx(2.0)
        assert policy.get_delay(3, TimeoutError()) == pytest.approx(4.0)

    def test_max_delay_capped(self):
        policy = RetryPolicy(backoff_factor=1.0, max_delay=5.0, jitter=False)
        assert policy.get_delay(10, TimeoutError()) == pytest.approx(5.0)

    def test_jitter_within_bounds(self):
        policy = RetryPolicy(backoff_factor=2.0, max_delay=100.0, jitter=True)
        for attempt in range(1, 5):
            d = policy.get_delay(attempt, TimeoutError())
            assert 0 <= d <= 100.0

    def test_retry_after_header_honored(self):
        policy = RetryPolicy(max_delay=60.0, jitter=False)
        error = RateLimitError("limited", retry_after=12.0)
        assert policy.get_delay(1, error) == pytest.approx(12.0)

    def test_retry_after_capped_by_max_delay(self):
        policy = RetryPolicy(max_delay=10.0, jitter=False)
        error = RateLimitError("limited", retry_after=999.0)
        assert policy.get_delay(1, error) == pytest.approx(10.0)


class TestExecute:
    async def test_success_first_try(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            return "ok"

        result = await RetryPolicy(max_retries=3).execute(fn)
        assert result == "ok"
        assert calls == 1

    async def test_retries_until_success(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            if calls < 3:
                raise TimeoutError("slow")
            return "done"

        policy = RetryPolicy(max_retries=5, backoff_factor=0.01, max_delay=0.05)
        result = await policy.execute(fn)
        assert result == "done"
        assert calls == 3

    async def test_gives_up_after_max_retries(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            raise TimeoutError("boom")

        policy = RetryPolicy(max_retries=2, backoff_factor=0.01, max_delay=0.05)
        with pytest.raises(TimeoutError):
            await policy.execute(fn)
        assert calls == 2

    async def test_does_not_retry_non_retryable(self):
        calls = 0

        async def fn():
            nonlocal calls
            calls += 1
            raise ValueError("bad")

        with pytest.raises(ValueError):
            await RetryPolicy(max_retries=3).execute(fn)
        assert calls == 1

    def test_retry_on_class_names(self):
        policy = RetryPolicy(max_retries=2, retry_on=["ValueError"])
        assert policy.should_retry(1, ValueError("x"))
