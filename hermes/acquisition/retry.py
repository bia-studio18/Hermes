from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

from hermes.core.errors import AcquisitionError, RateLimitError, ServerError, TimeoutError

logger = logging.getLogger(__name__)


class RetryPolicy(BaseModel):
    max_retries: int = 3
    backoff_factor: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retry_on: list[str] = Field(default_factory=list)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        if attempt >= self.max_retries:
            return False
        return self._is_retryable(error)

    def get_delay(self, attempt: int, error: Exception) -> float:
        if isinstance(error, RateLimitError) and error.retry_after is not None:
            return min(error.retry_after, self.max_delay)

        base = self.backoff_factor * (2 ** (attempt - 1))
        if self.jitter:
            base += random.SystemRandom().uniform(0, base * 0.5)
        return min(base, self.max_delay)

    async def execute(
        self,
        fn: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if not self.should_retry(attempt, exc):
                    raise
                delay = self.get_delay(attempt, exc)
                logger.warning(
                    "Retry %d/%d for %s – sleeping %.2fs (error: %s)",
                    attempt,
                    self.max_retries,
                    getattr(fn, "__name__", fn),
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
        raise AcquisitionError("Retry loop exhausted") from last_exc

    def _is_retryable(self, error: Exception) -> bool:
        if isinstance(error, (RateLimitError, TimeoutError, ServerError)):
            return True
        if isinstance(error, OSError):
            return True
        if isinstance(error, asyncio.TimeoutError):
            return True

        if self.retry_on:
            return type(error).__name__ in self.retry_on

        if isinstance(error, aiohttp.ClientError):
            return True

        return False
